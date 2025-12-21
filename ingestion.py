import feedparser
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
from vector_store import get_collection
from llm_summary_required import needs_llm_summary
from llm_backfill import backfill_llm_summaries

def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)

def generate_doc_id(url):
    return hashlib.sha256(url.encode()).hexdigest()

def fetch_stock_news_rss(ticker, limit=10):
    rss_url = (
        f"https://news.google.com/rss/search?"
        f"q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
    )

    feed = feedparser.parse(rss_url)
    documents = []

    for entry in feed.entries[:limit]:
        title = entry.title
        raw_summary = entry.get("summary", "")
        summary = clean_html(raw_summary)
        link = entry.link

        # Basic relevance guard
        if ticker.lower() not in (title + summary).lower():
            continue

        published = entry.get("published", "")
        try:
            publish_time = datetime.strptime(
                published, "%a, %d %b %Y %H:%M:%S %Z"
            )
        except ValueError:
            publish_time = datetime.now()

        base_id = generate_doc_id(link)

        # 🔹 NEW: summary quality check
        requires_llm = needs_llm_summary(title, summary)

        # If RSS summary is bad, store title only (for now)
        final_summary = summary if not requires_llm else ""
        print("TITLE:", title)
        print("Date:", publish_time)
        print("SUMMARY:", summary)
        print("NEEDS_LLM:", requires_llm)
        print("FINAL_SUMMARY:", final_summary)
        print("-" * 80)


        text = f"""
Stock: {ticker}
Title: {title}
Summary: {final_summary}
""".strip()

        documents.append({
            "id": base_id,
            "text": text,
            "metadata": {
                "ticker": ticker,
                "timestamp": publish_time.timestamp(),
                "date": publish_time.strftime("%Y-%m-%d %H:%M:%S"),
                "source_url": link,
                "content_type": "news",
                "summary_source": "rss" if not requires_llm else "needs_llm"
            }
        })

    return documents


def ingest_news(ticker):
    collection = get_collection()
    docs = fetch_stock_news_rss(ticker)

    if not docs:
        print("❌ No news found.")
        return

    existing = set(collection.get(ids=[doc["id"] for doc in docs])["ids"])
    new_docs = [doc for doc in docs if doc["id"] not in existing]

    if not new_docs:
        print("ℹ️ No new articles.")
        return

    collection.upsert(
        ids=[doc["id"] for doc in new_docs],
        documents=[doc["text"] for doc in new_docs],
        metadatas=[doc["metadata"] for doc in new_docs]
    )

    print(f"✅ Ingested {len(new_docs)} articles ({ticker})")
