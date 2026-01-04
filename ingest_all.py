from ingestion.asset_resolver import resolve_asset
from ingestion.google_news import fetch_google_news
from ingestion.price_summaries import fetch_price_summary
from ingestion.macro_markets import fetch_macro_docs
from ingestion.alphavantage_news import fetch_alphavantage_news
from ingestion.moneycontrol import fetch_moneycontrol_news
from vector_store import get_collection

ALPHAVANTAGE_API_KEY = "YOUR API KEY"

def ingest_all(symbol):
    asset = resolve_asset(symbol)
    collection = get_collection()

    print(
        f"🚀 Starting ingestion for {asset['symbol']} "
        f"({asset['asset_type']}, {asset['market']})"
    )

    docs = []

    # ---- EQUITY ----
    if asset["asset_type"] == "equity":
        print("🔹 Fetching Equity News (Google News)...")
        docs += fetch_google_news(asset["symbol"], asset["asset_type"])
        
        print("🔹 Fetching Equity News (AlphaVantage)...")
        docs += fetch_alphavantage_news(asset["symbol"], ALPHAVANTAGE_API_KEY)

        if asset["market"] == "IN":
            print("🔹 Fetching Equity News (MoneyControl)...")
            from ingestion.moneycontrol import fetch_moneycontrol_news
            docs += fetch_moneycontrol_news(asset["symbol"])

        print("🔹 Fetching Price Summary...")
        price_doc = fetch_price_summary(asset["symbol"], ALPHAVANTAGE_API_KEY)
        if price_doc:
            docs.append(price_doc)

    # ---- COMMODITY / FOREX ----
    elif asset["asset_type"] in ("commodity", "forex"):
        print("🔹 Fetching Macro News...")
        docs += fetch_macro_docs(ALPHAVANTAGE_API_KEY)
        
        print("🔹 Fetching Qualitative News (Google)...")
        docs += fetch_google_news(asset["symbol"], asset["asset_type"])

        print("🔹 Fetching Price Summary...")
        price_doc = fetch_price_summary(asset["symbol"], ALPHAVANTAGE_API_KEY)
        if price_doc:
            docs.append(price_doc)

    # ---- INDEX ----
    elif asset["asset_type"] == "index":
        print("🔹 Fetching Index News...")
        docs += fetch_google_news(asset["symbol"])

    else:
        print("⚠️ Unknown asset type, falling back to news only")
        docs += fetch_google_news(asset["symbol"])

    if not docs:
        print("❌ No documents collected.")
        return

    print(f"📊 Total documents collected: {len(docs)}")

    # ---- Deduplication ----
    # ---- Deduplication ----
    # Deduplicate within the batch (keep last occurrence)
    unique_docs_map = {d["id"]: d for d in docs}
    unique_docs = list(unique_docs_map.values())

    ids = [d["id"] for d in unique_docs]
    existing = set(collection.get(ids=ids)["ids"])
    new_docs = [d for d in unique_docs if d["id"] not in existing]

    if not new_docs:
        print("ℹ️ No new documents to insert.")
        return

    print(f"💾 Inserting {len(new_docs)} documents...")
    for i in docs:
        print(i["text"])
    collection.upsert(
        ids=[d["id"] for d in new_docs],
        documents=[d["text"] for d in new_docs],
        metadatas=[d["metadata"] for d in new_docs]
    )

    print(f"✅ Ingestion complete for {asset['symbol']}")
