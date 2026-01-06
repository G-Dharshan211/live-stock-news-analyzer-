import requests
import hashlib
from datetime import datetime

def generate_doc_id(seed: str):
    return hashlib.sha256(seed.encode()).hexdigest()

def fetch_price_summary(ticker, api_key):
    # Map common commodities to AlphaVantage symbols
    COMMODITY_MAP = {
        "GOLD": "XAUUSD",
        "SILVER": "XAGUSD",
        "CRUDE": "WTI",
        "OIL": "WTI"
    }
    
    query_symbol = COMMODITY_MAP.get(ticker.upper(), ticker)

    url = (
        "https://www.alphavantage.co/query"
        f"?function=TIME_SERIES_DAILY"
        f"&symbol={query_symbol}"
        f"&apikey={api_key}"
    )

    print(f"   💸 Fetching Price Summary for {ticker} (Query: {query_symbol})...")
    # print(f"   🔗 URL: {url}") # Careful printing API keys
    try:
        response = requests.get(url)
        data = response.json()
    except Exception as e:
        print(f"   ❌ Error fetching price data: {e}")
        return None

    ts = data.get("Time Series (Daily)", {})
    print(f"   📅 Data points: {len(ts)}")

    if len(ts) < 2:
        return None

    dates = list(ts.keys())[:5]
    start = float(ts[dates[-1]]["4. close"])
    end = float(ts[dates[0]]["4. close"])
    pct = ((end - start) / start) * 100

    direction = "rose" if pct > 0 else "fell"

    text = (
        f"{ticker} stock {direction} {abs(pct):.2f}% "
        f"over the past {len(dates)} trading days, "
        "reflecting recent market reaction."
    )

    title = f"{ticker} Price Update: {direction.capitalize()} {abs(pct):.2f}%"
    
    return {
    "id": generate_doc_id(ticker + dates[0]),
    "text": text,
    "metadata": {
        "title": title,
        "symbol": ticker,
        "asset_type": "commodity" if ticker == "XAUUSD" else "forex" if len(ticker) == 6 else "equity",
        "market": "IN" if ticker.endswith("INR") else "GLOBAL",
        "content_type": "price",
        "timestamp": datetime.now().timestamp(),
        "date": dates[0],
        "source": "alphavantage",
        "publisher": "AlphaVantage",
        "source_url": "alphavantage",
        "summary_source": "api"
    }
}

