from datetime import datetime, timedelta
from typing import List
from dotenv import load_dotenv

from vector_store import get_collection

# 🔹 IMPORT FROM MULTI-QUERY MODULE
from multiquery import (
    generate_llm_multi_queries,
    retrieve_multi_query_results,
    rrf_multi_query_fusion,
    extract_summary
)

load_dotenv()

# ===============================
# Prompt (hallucination-safe)
# ===============================
ANSWER_PROMPT = """
You are a financial assistant.

Answer the user's question using ONLY the information present
in the provided news summaries.

Rules:
- Do NOT add facts not present in the summaries.
- Do NOT speculate beyond what is stated.
- If information is incomplete or uncertain, say so clearly.
- Focus on recent performance and investor-relevant implications.
- Keep the answer concise and factual.

{context}

Final Answer:
"""

# ===============================
# Sentiment Words
# ===============================
NEGATIVE_WORDS = {
    "slides", "falls", "droops", "pressure", "concerns",
    "jitters", "uncertainty", "scrutiny", "weakness"
}

POSITIVE_WORDS = {
    "rises", "gains", "upgrades", "raises target",
    "bullish", "strong", "growth", "optimistic"
}

# ===============================
# Sentiment + Confidence
# ===============================
def infer_sentiment_and_confidence(summaries: List[str]):
    text = " ".join(summaries).lower()

    neg = sum(word in text for word in NEGATIVE_WORDS)
    pos = sum(word in text for word in POSITIVE_WORDS)

    if pos > neg:
        sentiment = "Positive"
    elif neg > pos:
        sentiment = "Negative"
    else:
        sentiment = "Mixed"

    if len(summaries) >= 3 and abs(pos - neg) >= 1:
        confidence = "High"
    elif len(summaries) >= 2:
        confidence = "Medium"
    else:
        confidence = "Low"

    return sentiment, confidence

# ===============================
# Context Builder
# ===============================
def build_answer_context(query: str, summaries: List[str]) -> str:
    summaries_text = "\n".join(
        [f"{i+1}. {s}" for i, s in enumerate(summaries)]
    )

    return f"""
User Question:
{query}

Recent News Summaries:
{summaries_text}
""".strip()

# ===============================
# CORE QUERY PIPELINE
# ===============================
def answer_user_query(
    query: str,
    llm,
    hours_lookback: int = 48,
    n_results: int = 5
) -> str:
    collection = get_collection()

    # 🔹 1. LLM Multi-Query Expansion
    queries = generate_llm_multi_queries(query, llm)

    # 🔹 2. Retrieve per query
    docs_per_query, _ = retrieve_multi_query_results(
        collection=collection,
        queries=queries,
        hours_lookback=hours_lookback,
        n_results=n_results
    )

    if not any(docs_per_query):
        return "There is insufficient recent information to answer this question."

    # 🔹 3. RRF Fusion (multi-query + intent)
    fused_docs = rrf_multi_query_fusion(
        docs_per_query,
        query,
        debug=False
    )


    # 🔹 4. Extract summaries
    summaries = [
        extract_summary(doc)
        for doc in fused_docs
        if extract_summary(doc)
    ]

    if not summaries:
        return "Recent news coverage does not provide enough detail to assess this."

    # 🔹 5. Sentiment & confidence
    sentiment, confidence = infer_sentiment_and_confidence(summaries)

    # 🔹 6. LLM Answer Generation
    context = build_answer_context(query, summaries)
    prompt = ANSWER_PROMPT.format(context=context)

    response = llm.invoke(prompt)

    final_answer = f"""{response.content.strip()}

Overall sentiment: {sentiment}
Confidence level: {confidence}
"""

    return final_answer.strip()

# ===============================
# Example Run
# ===============================
"""if __name__ == "__main__":
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )

    query = "how does NVDIA perform"

    answer = answer_user_query(
        query=query,
        llm=llm,
        hours_lookback=48,
        n_results=5
    )

    print("\n📊 Answer:\n")
    print(answer)"""
