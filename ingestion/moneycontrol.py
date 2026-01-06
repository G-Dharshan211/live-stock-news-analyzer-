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

def build_moneycontrol_query(symbol):
    # Restrict search to moneycontrol.com
    return f"site:moneycontrol.com {symbol}"

def fetch_moneycontrol_news(symbol, limit=10):
    """
    Fetches news for a symbol specifically from MoneyControl using Google News RSS proxy.
    """
    query = build_moneycontrol_query(symbol)
    encoded_query = quote_plus(query)
    
    rss_url = (
        f"https://news.google.com/rss/search?"
        f"q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
    )

    print(f"   📰 Fetching MoneyControl News (via Google RSS) for {symbol}...")
    
    try:
        feed = feedparser.parse(rss_url)
    except Exception as e:
        print(f"   ❌ Error checking RSS feed: {e}")
        return []

    if not feed.entries:
        print("   ⚠️ No articles found on MoneyControl.")
        return []

    print(f"   ✅ Found {len(feed.entries)} articles from MoneyControl")

    documents = []
    for entry in feed.entries[:limit]:
        title = clean_html(entry.title)
        link = entry.link
        published = entry.published
        summary = clean_html(entry.summary) if "summary" in entry else ""
        
        # Parse date
        try:
            dt = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z")
            timestamp = dt.timestamp()
        except Exception:
            timestamp = datetime.now().timestamp()
            
        doc_id = generate_doc_id(link)

        # MoneyControl specific reliable source check
        # (Though we filtered by site, double check source title if available)
        source_title = entry.source.title if "source" in entry else "MoneyControl"

        # Determine if we need LLM summary
        requires_llm = needs_llm_summary(title, summary)
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
                "symbol": symbol,
                "title": title,
                "source_url": link,
                "source": "MoneyControl",
                "publisher": "MoneyControl",
                "content_type": "news",
                "timestamp": timestamp,
                "date": str(datetime.fromtimestamp(timestamp)),
                "summary_source": "rss" if not requires_llm else "needs_llm"
            }
        })

    return documents
