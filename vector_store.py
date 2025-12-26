import chromadb
from chromadb.utils import embedding_functions

DB_PATH = "./stock_news_db"
COLLECTION_NAME = "financial_news"

def get_collection():
    client = chromadb.PersistentClient(path=DB_PATH)

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn
    )

    return collection

def delete_news_for_ticker(ticker):
    """Deletes all news articles for a given ticker from the DB."""
    collection = get_collection()
    print(f"🗑️ Deleting news for {ticker}...")
    try:
        collection.delete(
            where={"ticker": ticker}
        )
        print(f"✅ Deleted news for {ticker}")
    except Exception as e:
        print(f"❌ Error deleting news for {ticker}: {e}")
