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
