from ingestion import ingest_news
from query import answer_user_query
from langchain_groq import ChatGroq
from llm_backfill import backfill_llm_summaries

if __name__ == "__main__":
    TICKER = "AMZN"
    # Step 1: Ingest latest news
    ingest_news(TICKER)

    backfill_llm_summaries(limit=4)
    # Step 2: Query recent news
    llm=ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

    answer = answer_user_query(
        query="how does Amazon perform",
        llm=llm,
        hours_lookback=120,
        n_results=3
    )
    print("\n📊 Answer:\n")
    print(answer)