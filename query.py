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
# Sentiment Weights
# ===============================
NEGATIVE_WEIGHTS = {
    "slides": 2, "falls": 2, "fell": 2, "drops": 2,
    "declines": 2, "pressure": 1, "concerns": 1,
    "uncertainty": 1, "scrutiny": 1, "weakness": 1,
    "selloff": 3
}

POSITIVE_WEIGHTS = {
    "rises": 2, "rose": 2, "gains": 2, "surges": 3,
    "jumps": 2, "upgrades": 3, "raises target": 3,
    "bullish": 2, "strong": 1, "growth": 1,
    "optimism": 1
}

HEDGING_WORDS = {"could", "might", "may", "potential", "possibly"}

# ===============================
# Sentiment + Confidence
# ===============================
def score_sentiment(summaries):
    score = 0
    for s in summaries:
        text = s.lower()
        for w, wt in POSITIVE_WEIGHTS.items():
            score += wt * text.count(w)
        for w, wt in NEGATIVE_WEIGHTS.items():
            score -= wt * text.count(w)
    return score

def hedging_penalty(summaries):
    return sum(
        s.lower().count(w)
        for s in summaries
        for w in HEDGING_WORDS
    )

def infer_sentiment_and_confidence(summaries):
    sentiment_score = score_sentiment(summaries)
    hedge_penalty = hedging_penalty(summaries)
    effective_score = abs(sentiment_score) - hedge_penalty

    if sentiment_score >= 3:
        sentiment = "Positive"
    elif sentiment_score <= -3:
        sentiment = "Negative"
    else:
        sentiment = "Mixed"

    if effective_score >= 5 and len(summaries) >= 3:
        confidence = "High"
    elif effective_score >= 3 and len(summaries) >= 2:
        confidence = "Medium"
    else:
        confidence = "Low"

    return sentiment, confidence

# ===============================
# Evidence helpers
# ===============================
def extract_key_evidence_with_links(docs, metas, max_points=3):
    evidence = []
    seen = set()

    for doc, meta in zip(docs, metas):
        if len(evidence) >= max_points:
            break

        summary = extract_summary(doc)
        link = meta.get("source_url", meta.get("url", ""))

        if summary and summary not in seen:
            evidence.append((summary, link))
            seen.add(summary)

    return evidence

def build_evidence_html(evidence):
    return "<br><br>".join(
        f"• {s}<br>&nbsp;&nbsp;🔗 <a href=\"{l}\" target=\"_blank\">Read article</a>"
        if l else f"• {s}"
        for s, l in evidence
    )

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
def answer_user_query_internal(
    query: str,
    llm,
    hours_lookback: int = 48,
    n_results: int = 5
):
    collection = get_collection()

    #  Multi-query expansion
    queries = generate_llm_multi_queries(query, llm)

    #  Retrieval
    docs_per_query, metas_per_query = retrieve_multi_query_results(
        collection=collection,
        queries=queries,
        hours_lookback=hours_lookback,
        n_results=n_results
    )

    if not any(docs_per_query):
        return "There is insufficient recent information to answer this question.", "Neutral", "Low", [], []

    #  RRF fusion
    fused_docs, fused_metas = rrf_multi_query_fusion(
        docs_per_query=docs_per_query,
        metas_per_query=metas_per_query,
        query=query,
        debug=False
    )

    summaries = [extract_summary(d) for d in fused_docs if extract_summary(d)]
    if not summaries:
        return "Recent news coverage does not provide enough detail to assess this.", "Neutral", "Low", [], []

    #  Sentiment & confidence
    sentiment, confidence = infer_sentiment_and_confidence(summaries)

    #  Evidence
    evidence = extract_key_evidence_with_links(fused_docs, fused_metas)
    evidence_html = build_evidence_html(evidence)

    #  Answer generation
    context = build_answer_context(query, summaries)
    response = llm.invoke(ANSWER_PROMPT.format(context=context))

    # Format evidence for API response
    evidence_list = [
        {"summary": s, "source_url": l}
        for s, l in evidence
    ]

    # Format news for API response
    news_list = [
        {
            "title": m.get("title", ""),
            "url": m.get("source_url", m.get("url", "")),
            "timestamp": m.get("date", ""),
            "source": m.get("source", "")
        }
        for m in fused_metas
    ][:5]  # Limit to top 5 live news items

    return (
        response.content.strip(),
        sentiment,
        confidence,
        evidence_list,
        news_list
    )

def answer_user_query(
    query: str,
    llm,
    hours_lookback: int = 48,
    n_results: int = 5
) -> str:
    """CLI/Text-only wrapper for backward compatibility"""
    answer, sentiment, confidence, evidence, news = answer_user_query_internal(
        query, llm, hours_lookback, n_results
    )
    
    evidence_html = build_evidence_html([(e["summary"], e["source_url"]) for e in evidence])
    
    return f"""{answer}

Overall sentiment: {sentiment}
Confidence level: {confidence}

Key evidence:
{evidence_html}
"""

def answer_user_query_json(
    query: str,
    hours_lookback: int = 48,
    n_results: int = 5
):
    from langchain_groq import ChatGroq
    
    # Initialize LLM (Gemini)
    
    llm=ChatGroq(model="llama-3.3-70b-versatile", temperature=0)


    # Use internal pipeline
    answer_text, sentiment, confidence, evidence, news = answer_user_query_internal(
        query=query,
        llm=llm,
        hours_lookback=hours_lookback,
        n_results=n_results
    )

    return {
        "answer": answer_text,
        "sentiment": sentiment,
        "confidence": confidence,
        "evidence": evidence,
        "news": news
    }
