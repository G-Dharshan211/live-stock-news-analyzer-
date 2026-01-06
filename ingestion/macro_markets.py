from ingestion.price_summaries import fetch_price_summary

def fetch_macro_docs(api_key):
    docs = []

    # ---- GOLD ----
    gold = fetch_price_summary("XAUUSD", api_key)
    if gold:
        gold["metadata"].update({
            "symbol": "GOLD",
            "asset_type": "commodity",
            "market": "GLOBAL",
            "content_type": "macro",
            "source": "alphavantage"
        })
        docs.append(gold)

    # ---- USDINR ----
    usd_inr = fetch_price_summary("USDINR", api_key)
    if usd_inr:
        usd_inr["metadata"].update({
            "symbol": "USDINR",
            "asset_type": "forex",
            "market": "IN",
            "content_type": "macro",
            "source": "alphavantage"
        })
        docs.append(usd_inr)

    # ---- EURUSD ----
    eur_usd = fetch_price_summary("EURUSD", api_key)
    if eur_usd:
        eur_usd["metadata"].update({
            "symbol": "EURUSD",
            "asset_type": "forex",
            "market": "GLOBAL",
            "content_type": "macro",
            "source": "alphavantage"
        })
        docs.append(eur_usd)

    return docs

