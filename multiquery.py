from datetime import datetime, timedelta
from collections import defaultdict

# ==============================
# LLM Multi-Query Prompt
# ==============================
MULTI_QUERY_PROMPT = """
You are helping expand a search query.

Generate alternative search queries that:
- Mean the same thing as the original query
- Use different wording or investor language
- Do NOT add new facts
- Do NOT speculate
- Do NOT mention prices or numbers

Original query:
"{query}"

Return 4 to 6 short search queries.
Each query should be on a new line.
"""

# ==============================
# Performance & Speculation Words
# ==============================

NEGATIVE_PERFORMANCE_WORDS = {
    "slides", "falls", "fell", "drops", "declines",
    "pressure", "jitters", "concerns", "uncertainty",
    "scrutiny", "weakness", "selloff"
}

POSITIVE_PERFORMANCE_WORDS = {
    "rises", "rose", "gains", "surges", "jumps",
    "upgrades", "raises target", "bullish",
    "strong", "optimism", "growth"
}

SPECULATIVE_WORDS = {
    "could", "might", "may", "potential", "possibly", "ipo"
}

# ==============================
# Intent Detection
# ==============================
def detect_intent(query: str) -> str:
    q = query.lower()

    if any(w in q for w in ["perform", "performance", "today", "now"]):
        return "performance"

    if any(w in q for w in ["why", "reason", "cause"]):
        return "cause"

    if any(w in q for w in ["outlook", "future", "expect"]):
        return "outlook"

    return "general"

# ==============================
# LLM Multi-Query Generator
# ==============================
def generate_llm_multi_queries(query: str, llm, max_queries=5):
    response = llm.invoke(
        MULTI_QUERY_PROMPT.format(query=query)
    )

    lines = [
        q.strip("-• ").strip()
        for q in response.content.splitlines()
        if len(q.strip()) > 10
    ]

    queries = [query] + lines

    # Deduplicate & limit
    seen = set()
    final = []
    for q in queries:
        ql = q.lower()
        if ql not in seen:
            final.append(q)
            seen.add(ql)
        if len(final) >= max_queries:
            break

    return final

# ==============================
# Retrieval per Query
# ==============================
def retrieve_multi_query_results(collection, queries, hours_lookback, n_results):
    cutoff = (datetime.now() - timedelta(hours=hours_lookback)).timestamp()

    all_docs = []
    all_metas = []

    for q in queries:
        results = collection.query(
            query_texts=[q],
            n_results=n_results,
            where={"timestamp": {"$gte": cutoff}}
        )

        all_docs.append(results.get("documents", [[]])[0])
        all_metas.append(results.get("metadatas", [[]])[0])

    return all_docs, all_metas

# ==============================
# RRF Core
# ==============================
def reciprocal_rank_fusion(rankings, k=60):
    scores = defaultdict(float)

    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] += 1 / (k + rank + 1)

    return sorted(scores.keys(), key=lambda d: scores[d], reverse=True)

# ==============================
# Utilities
# ==============================
def extract_summary(doc: str) -> str:
    for line in doc.splitlines():
        if line.startswith("Summary:"):
            return line.replace("Summary:", "").strip()
    return ""

# ==============================
# Intent-based Summary Scoring
# ==============================
def score_summary_for_intent(summary: str, intent: str) -> int:
    text = summary.lower()
    score = 0

    if intent == "performance":
        for w in POSITIVE_PERFORMANCE_WORDS:
            score += text.count(w)
        for w in NEGATIVE_PERFORMANCE_WORDS:
            score -= text.count(w)
        for w in SPECULATIVE_WORDS:
            score -= text.count(w)

    return score

# ==============================
# RRF Fusion Across Multi-Query + Intent
# ==============================
def rrf_multi_query_fusion(docs_per_query, query, debug=False):
    intent = detect_intent(query)

    doc_map = {}
    rankings = []
    idx = 0

    for docs in docs_per_query:
        ids = []
        for doc in docs:
            if doc not in doc_map:
                doc_map[doc] = idx
                idx += 1
            ids.append(doc_map[doc])
        rankings.append(ids)

    intent_rank = sorted(
        doc_map.keys(),
        key=lambda d: score_summary_for_intent(
            extract_summary(d),
            intent
        ),
        reverse=True
    )

    rankings.append([doc_map[d] for d in intent_rank])

    # 🔍 Visualization hook
    if debug:
        visualize_rrf_debug(
            doc_map=doc_map,
            rankings=rankings
        )

    fused_ids = reciprocal_rank_fusion(rankings)
    inverse_map = {v: k for k, v in doc_map.items()}

    return [inverse_map[i] for i in fused_ids]

def compute_rrf_scores(rankings, k=60):
    """
    Compute RRF scores and per-signal contributions.
    """
    scores = defaultdict(float)
    contributions = defaultdict(list)

    for signal_idx, ranking in enumerate(rankings):
        for rank, doc_id in enumerate(ranking):
            score = 1 / (k + rank + 1)
            scores[doc_id] += score
            contributions[doc_id].append(
                {
                    "signal": signal_idx,
                    "rank": rank + 1,
                    "score": round(score, 5)
                }
            )

    return scores, contributions

def visualize_rrf_debug(doc_map, rankings, k=60, max_docs=5):
    scores, contributions = compute_rrf_scores(rankings, k)

    inverse_map = {v: k for k, v in doc_map.items()}

    print("\n📊 RRF DEBUG VIEW")
    print("=" * 70)

    for doc_id in sorted(scores, key=lambda d: scores[d], reverse=True)[:max_docs]:
        doc = inverse_map[doc_id]
        summary = extract_summary(doc)

        print("\n📰 Document Summary:")
        print(summary[:140] + ("..." if len(summary) > 140 else ""))
        print(f"Final RRF Score: {scores[doc_id]:.5f}")

        for c in contributions[doc_id]:
            print(
                f"  • Signal {c['signal']} → rank {c['rank']}, "
                f"contribution {c['score']}"
            )
