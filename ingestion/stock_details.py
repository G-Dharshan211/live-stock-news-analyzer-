import yfinance as yf
import traceback

def fetch_stock_details(ticker: str):
    """
    Fetches detailed financial metrics for a stock using yfinance.
    Returns a dictionary with:
    - current_price, high, low, volume
    - pe_ratio, roe, profit_margin
    - market_cap, sector
    """
    print(f"   📊 Fetching details for {ticker} via yfinance...")
    
    # Handle Indian stocks suffix if missing
    # yfinance uses '.NS' for NSE and '.BO' for BSE. 
    # Our app often uses plain tickers for US or 'IN' market logic.
    # We'll try plain ticker first, then add suffixes if needed.
    
    try:
        y_ticker = ticker
        
        # If it's likely an Indian stock but no suffix (simple heuristic or passed context preferred)
        # For now, we relies on simple try/fallback or just raw ticker if standard.
        # Common convention in this codebase seems to be "ITC", "RELIANCE" without .NS for internal use,
        # but yfinance DEFINITELY needs .NS or .BO for Indian stocks.
        


        # We will try the ticker as is. If data is missing, we might try appending .NS for common Indian stocks
        stock = yf.Ticker(y_ticker)
        info = stock.info
        
        # If 'regularMarketPrice' is missing, it might be the wrong ticker format.
        if "regularMarketPrice" not in info and "currentPrice" not in info:
            if not ticker.endswith(".NS") and not ticker.endswith(".BO"):
                 print(f"   ⚠️ Possible missing Indian suffix for {ticker}, trying {ticker}.NS...")
                 stock = yf.Ticker(f"{ticker}.NS")
                 info = stock.info
        
        # Extract metrics
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
        day_high = info.get("dayHigh") or info.get("regularMarketDayHigh")
        day_low = info.get("dayLow") or info.get("regularMarketDayLow")
        volume = info.get("volume") or info.get("regularMarketVolume")
        
        pe_ratio = info.get("trailingPE") or info.get("forwardPE")
        roe = info.get("returnOnEquity")
        profit_margin = info.get("profitMargins")
        market_cap = info.get("marketCap")
        
        # Calculate raw change and ROI (daily return)
        change = 0.0
        roi = 0.0
        if current_price and previous_close:
            change = current_price - previous_close
            roi = (change / previous_close) * 100
            
        data = {
            "symbol": ticker,
            "price": current_price,
            "change": change,
            "change_percent": roi, # We'll treat daily change % as a proxy for immediate ROI context or just Label it Change %
            "high": day_high,
            "low": day_low,
            "volume": volume,
            "pe_ratio": pe_ratio,
            "roe": roe,
            "profit_margin": profit_margin,
            "market_cap": market_cap,
            "currency": info.get("currency"),
            "company_name": info.get("longName")
        }
        
        print(f"   ✅ Successfully fetched details for {ticker}")
        return data

    except Exception as e:
        print(f"   ❌ Error fetching yfinance data for {ticker}: {e}")
        traceback.print_exc()
        return None
