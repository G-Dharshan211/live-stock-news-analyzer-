import yfinance as yf
from datetime import datetime
import hashlib

def generate_doc_id(seed: str):
    return hashlib.sha256(seed.encode()).hexdigest()

def fetch_yfinance_news(ticker):
    """
    Fetches news from yfinance for a specific ticker.
    """
    print(f"   📡 Fetching yfinance News for {ticker}...")
    
    try:
        # Check if we need .NS suffix for news? 
        # yfinance usually attaches news to the base ticker object.
        # But if it's explicitly an Indian stock, using the .NS ticker is safer.
        
        # We can rely on the fact that ingest_all usually resolves the symbol.
        # However, yfinance news is often attached to the specific region ticker.
        
        # Quick check if it looks like an Indian ticker without suffix, try adding it.
        # But ingest_all passes the "symbol" from asset_resolver which might be "ITC" (Equity, Market: IN).
        # We should use .NS if market is IN. But standard yf.Ticker("ITC.NS") works.
        
        # Let's try to infer if suffix is needed or just attempt both?
        # A simple robust way: Just use the ticker provided. 
        # If the caller (ingest_all) passes "ITC" and market is IN, it might be better to pass "ITC.NS".
        # But let's assume the caller handles the suffix or we try both if needed.
        
        # Actually, let's just use the ticker as is first.
        stock = yf.Ticker(ticker)
        news_items = stock.news
        
        # If no news and it looks like it could be Indian, try .NS
        if not news_items and not ticker.endswith(".NS") and not ticker.endswith(".BO"):
             # Heuristic check - if we simply don't get news, maybe try .NS
             pass 

        documents = []
        if not news_items:
             print(f"   ⚠️ No news found via yfinance for {ticker}")
             return []

        for item in news_items:
            # yfinance news item structure:
            # {
            #   "uuid": "...",
            #   "title": "...",
            #   "publisher": "...",
            #   "link": "...",
            #   "providerPublishTime": 123456789,
            #   "type": "STORY",
            #   ...
            # }
            
            title = item.get("title", "")
            url = item.get("link", "")
            publisher = item.get("publisher", "yfinance")
            publish_time = item.get("providerPublishTime", 0)
            
            # Skip if no URL
            if not url:
                continue

            try:
                dt = datetime.fromtimestamp(publish_time)
                date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                dt = datetime.now()
                date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            
            text = f"""
Asset: {ticker}
Title: {title}
Source: {publisher}
Date: {date_str}
Summary: (See link for details)
""".strip()
            
            doc_id = generate_doc_id(url + ticker)
            
            documents.append({
                "id": doc_id,
                "text": text,
                "metadata": {
                    "symbol": ticker,
                    "title": title,
                    "source_url": url,
                    "source": "yfinance",
                    "publisher": publisher,
                    "content_type": "news",
                    "timestamp": float(publish_time),
                    "date": date_str,
                    "summary_source": "api"
                }
            })
            
        print(f"   ✅ Fetched {len(documents)} news items from yfinance")
        return documents

    except Exception as e:
        print(f"   ❌ Error fetching yfinance news: {e}")
        return []
