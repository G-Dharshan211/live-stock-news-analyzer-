import feedparser
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from llm_summary_required import needs_llm_summary

def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)

def generate_doc_id(seed: str):
    return hashlib.sha256(seed.encode()).hexdigest()

def build_news_query(symbol, asset_type):
    if asset_type == "equity":
        return f"{symbol}"
    if asset_type == "commodity":
        return "gold price india inflation interest rates"
    if asset_type == "forex":
        return f"{symbol} exchange rate rbi dollar"
    if asset_type == "index":
        return f"{symbol} market today"
    return symbol

def fetch_google_news(symbol, asset_type, limit=10):
    query = build_news_query(symbol, asset_type)

    encoded_query = quote_plus(query)
    rss_url = (
        f"https://news.google.com/rss/search?"
        f"q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
    )

    print(f"🔎 Google News query: {query}")
    feed = feedparser.parse(rss_url)

    documents = []

    for entry in feed.entries[:limit]:
        title = entry.title
        summary = clean_html(entry.get("summary", ""))
        link = entry.link

        published = entry.get("published", "")
        try:
            publish_time = datetime.strptime(
                published, "%a, %d %b %Y %H:%M:%S %Z"
            )
        except ValueError:
            publish_time = datetime.now()


        doc_id = generate_doc_id(link)

        # Check if RSS summary needs LLM enhancement
        requires_llm = needs_llm_summary(title, summary)
        
        # If summary is poor quality, store empty summary for LLM backfill
        final_summary = summary if not requires_llm else ""

        text = f"""
Asset: {symbol}
Title: {title}
Summary: {final_summary}
""".strip()

        documents.append({
            "id": doc_id,
            "text": text,
            "metadata": {
                "title": title,
                "symbol": symbol,
                "asset_type": asset_type,
                "market":"IN",
                "timestamp": publish_time.timestamp(),
                "date": publish_time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": "Google News",
                "publisher": "Google News",
                "source_url": link,
                "content_type": "news",
                "summary_source": "rss" if not requires_llm else "needs_llm"
            }
        })

    return documents
