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
NEGATIVE_WEIGHTS = {
    "slides": 2,
    "falls": 2,
    "fell": 2,
    "drops": 2,
    "declines": 2,
    "pressure": 1,
    "concerns": 1,
    "uncertainty": 1,
    "scrutiny": 1,
    "weakness": 1,
    "selloff": 3
}

POSITIVE_WEIGHTS = {
    "rises": 2,
    "rose": 2,
    "gains": 2,
    "surges": 3,
    "jumps": 2,
    "upgrades": 3,
    "raises target": 3,
    "bullish": 2,
    "strong": 1,
    "growth": 1,
    "optimism": 1
}

HEDGING_WORDS = {
    "could", "might", "may", "potential", "possibly"
}

def score_sentiment(summaries):
    """
    Returns a signed sentiment score.
    Positive = bullish bias
    Negative = bearish bias
    """
    score = 0

    for s in summaries:
        text = s.lower()

        for w, wt in POSITIVE_WEIGHTS.items():
            score += wt * text.count(w)

        for w, wt in NEGATIVE_WEIGHTS.items():
            score -= wt * text.count(w)

    return score

def hedging_penalty(summaries):
    penalty = 0
    for s in summaries:
        text = s.lower()
        for w in HEDGING_WORDS:
            penalty += text.count(w)
    return penalty

# ===============================
# Sentiment + Confidence
# ===============================
def infer_sentiment_and_confidence(summaries):
    sentiment_score = score_sentiment(summaries)
    hedge_penalty = hedging_penalty(summaries)

    # ---- Sentiment label ----
    if sentiment_score >= 3:
        sentiment = "Positive"
    elif sentiment_score <= -3:
        sentiment = "Negative"
    else:
        sentiment = "Mixed"

    # ---- Confidence logic ----
    effective_score = abs(sentiment_score) - hedge_penalty

    if effective_score >= 5 and len(summaries) >= 3:
        confidence = "High"
    elif effective_score >= 3 and len(summaries) >= 2:
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
