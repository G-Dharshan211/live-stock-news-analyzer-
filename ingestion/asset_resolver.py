# ingestion/asset_resolver.py

import re
import yfinance as yf

FOREX_PATTERNS = [
    r"^[A-Z]{6}$",        # EURUSD, USDINR
    r"^[A-Z]{3}INR$",     # USDINR
]

COMMODITIES = {
    "GOLD", "SILVER", "CRUDE", "OIL", "NATGAS"
}

INDICES = {
    "NIFTY", "SENSEX", "BANKNIFTY"
}


def resolve_asset(symbol: str):
    s = symbol.upper().strip()

    # ---- Commodity ----
    if s in COMMODITIES:
        return {
            "symbol": s,
            "asset_type": "commodity",
            "market": "GLOBAL"
        }
    # ---- Forex ----
    for pattern in FOREX_PATTERNS:
        if re.match(pattern, s):
            return {
                "symbol": s,
                "asset_type": "forex",
                "market": "IN" if s.endswith("INR") else "GLOBAL"
            }

    # ---- Index ----
    if s in INDICES:
        return {
            "symbol": s,
            "asset_type": "index",
            "market": "IN"
        }

    # ---- Equity (default) ----
    # ---- Equity (default) ----
    # Attempt auto-detection using yfinance
    market = "UNKNOWN"
    try:
        # Check standard ticker first
        ticker = s
        info = yf.Ticker(ticker).info
        currency = info.get("currency", "")
        
        # If not found or no currency, try .NS (common for India)
        if not currency or (currency != "INR" and "regularMarketPrice" not in info):
             info_ns = yf.Ticker(f"{s}.NS").info
             if info_ns and info_ns.get("currency") == "INR":
                 market = "IN"
             elif currency == "INR":
                 market = "IN"
             else:
                 market = "GLOBAL" if currency else "UNKNOWN"
        elif currency == "INR":
            market = "IN"
        elif currency in ["USD", "EUR", "GBP"]:
             market = "GLOBAL"

    except Exception:
        # Fallback if network/yfinance fails
        pass

    return {
        "symbol": s,
        "asset_type": "equity",
        "market": market
    }
