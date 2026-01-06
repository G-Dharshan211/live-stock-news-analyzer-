import requests
import hashlib
from datetime import datetime

def generate_doc_id(seed: str):
    return hashlib.sha256(seed.encode()).hexdigest()

def fetch_alphavantage_news(ticker, api_key, limit=5):
    """
    Fetches news sentiment data from AlphaVantage for a specific ticker.
    """
    
    url = (
        "https://www.alphavantage.co/query"
        f"?function=NEWS_SENTIMENT"
        f"&tickers={ticker}"
        f"&limit={limit}"
        f"&apikey={api_key}"
    )
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Check for API errors or limit messages
        if "Note" in data:
            print(f"   ⚠️ AlphaVantage API Note: {data['Note']}")
        if "Information" in data:
            pass
            
        feed = data.get("feed", [])

        if not feed and ("IN" in ticker or ticker in ["ITC", "HDFCBANK", "RELIANCE", "NATIONALUM", "KTKBANK"]):
            # Retry with .BSE suffix for Indian stocks if no news found
            print(f"   ⚠️ No news for {ticker}, retrying with {ticker}.BSE...")
            url = (
                "https://www.alphavantage.co/query"
                f"?function=NEWS_SENTIMENT"
                f"&tickers={ticker}.BSE"
                f"&limit={limit}"
                f"&apikey={api_key}"
            )
            try:
                response = requests.get(url)
                data = response.json()
                feed = data.get("feed", [])
            except Exception as e:
                print(f"   ❌ Retry failed: {e}")

        documents = []
        for item in feed:
            title = item.get("title", "")
            summary = item.get("summary", "")
            source = item.get("source", "AlphaVantage")
            url = item.get("url", "")
            published_str = item.get("time_published", "")
            
            # Parse timestamp (Format: YYYYMMDDTHHMMSS)
            try:
                dt = datetime.strptime(published_str, "%Y%m%dT%H%M%S")
                timestamp = dt.timestamp()
            except ValueError:
                timestamp = datetime.now().timestamp()
            
            # Check relevance score for this ticker
            relevance_score = 0.0
            sentiment_score = 0.0
            sentiment_label = "Neutral"
            
            for ticker_sentiment in item.get("ticker_sentiment", []):
                if ticker_sentiment.get("ticker") == ticker:
                    relevance_score = float(ticker_sentiment.get("relevance_score", 0))
                    sentiment_score = float(ticker_sentiment.get("ticker_sentiment_score", 0))
                    sentiment_label = ticker_sentiment.get("ticker_sentiment_label", "Neutral")
                    break
            
            # Filter low relevance news if needed (e.g., < 0.1)
            if relevance_score < 0.15:
                continue

            # Create document text
            text = f"""
Asset: {ticker}
Title: {title}
Summary: {summary}
Sentiment: {sentiment_label} (Score: {sentiment_score})
""".strip()
            
            doc_id = generate_doc_id(url + ticker)
            
            documents.append({
                "id": doc_id,
                "text": text,
                "metadata": {
                    "symbol": ticker,
                    "title": title,
                    "source_url": url,
                    "source": source,
                    "publisher": source,
                    "content_type": "news",
                    "timestamp": timestamp,
                    "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "summary_source": "api",  # Already summarized by AlphaVantage
                    "relevance_score": relevance_score,
                    "sentiment_score": sentiment_score,
                    "sentiment_label": sentiment_label
                }
            })
            

        return documents
        
    except Exception as e:
        print(f"   ❌ Error fetching AlphaVantage news: {e}")
        return []
