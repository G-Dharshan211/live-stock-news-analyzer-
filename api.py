from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import os
from dotenv import load_dotenv
load_dotenv()

from ingest_all import ingest_all
from query import answer_user_query_json
from vector_store import delete_news_for_ticker
from ingestion.stock_details import fetch_stock_details
# from llm_backfill import backfill_llm_summaries # Imported dynamically where needed


# -----------------------
# FastAPI App
# -----------------------
app = FastAPI(
    title="Traders Paradise API",
    version="1.0.0"
)

# -----------------------
# CORS (React support)
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Models
# -----------------------
class QueryRequest(BaseModel):
    question: str
    ticker: str = None  # Optional ticker for context injection
    hours_lookback: int = 120  # Default to 5 days matching backend capability

class Evidence(BaseModel):
    summary: str
    source_url: str

class NewsItem(BaseModel):
    title: str
    url: str
    timestamp: str
    source: str

class StockResponse(BaseModel):
    answer: str
    sentiment: str
    confidence: str
    evidence: List[Evidence]
    news: List[NewsItem]

class IngestRequest(BaseModel):
    ticker: str

class WatchlistRequest(BaseModel):
    ticker: str

# -----------------------
# Persistent Watchlist
# -----------------------
WATCHLIST_FILE = "watchlist.json"
DEFAULT_WATCHLIST = ["ITC", "AAPL", "GOOGL","RELIANCE"]

def load_watchlist():
    if not os.path.exists(WATCHLIST_FILE):
        save_watchlist(DEFAULT_WATCHLIST)
        return DEFAULT_WATCHLIST
    try:
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)
    except:
        return DEFAULT_WATCHLIST

def save_watchlist(watchlist):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(watchlist, f)

# -----------------------
# Background Tasks
# -----------------------
def ingest_all_watchlist(watchlist: List[str]):
    print("🚀 Triggering background ingestion for watchlist...")
    for ticker in watchlist:
        try:
            ingest_all(ticker)
        except Exception as e:
            print(f"⚠️ Failed to ingest {ticker}: {e}")
    print("✅ Background ingestion complete.")

def ingest_single_ticker(ticker: str):
    try:
        ingest_all(ticker)
    except Exception as e:
        print(f"⚠️ Failed to ingest {ticker}: {e}")

def remove_single_ticker_data(ticker: str):
    try:
        delete_news_for_ticker(ticker)
    except Exception as e:
        print(f"⚠️ Failed to remove data for {ticker}: {e}")

@app.post("/api/query", response_model=StockResponse)
def query_from_search(req: QueryRequest):
    try:
        return answer_user_query_json(
            query=req.question,
            hours_lookback=req.hours_lookback,
            n_results=5,
            ticker=req.ticker
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/watchlist")
def get_watchlist(background_tasks: BackgroundTasks):
    current_list = load_watchlist()
    # Trigger ingestion for all stocks in the background when dashboard loads
    background_tasks.add_task(ingest_all_watchlist, current_list)
    return current_list

@app.post("/api/watchlist/add")
def add_to_watchlist(req: WatchlistRequest, background_tasks: BackgroundTasks):
    current_list = load_watchlist()
    ticker = req.ticker.upper()
    
    if ticker not in current_list:
        current_list.append(ticker)
        save_watchlist(current_list)
        # Trigger ingestion for the new stock
        background_tasks.add_task(ingest_single_ticker, ticker)
        
    return current_list

@app.post("/api/watchlist/remove")
def remove_from_watchlist(req: WatchlistRequest, background_tasks: BackgroundTasks):
    current_list = load_watchlist()
    ticker = req.ticker.upper()
    
    if ticker in current_list:
        current_list.remove(ticker)
        save_watchlist(current_list)
        # Trigger data cleanup for the removed stock
        background_tasks.add_task(remove_single_ticker_data, ticker)
        
    return current_list

@app.post("/api/ingest")
def ingest_stock_news(req: IngestRequest):
    try:
        ingest_all(req.ticker.upper())
        return {"status": "success", "ticker": req.ticker.upper()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stocks/{ticker}", response_model=StockResponse)
def get_stock_info(ticker: str):
    try:
        result = answer_user_query_json(
            query=f"how does {ticker.upper()} perform",
            hours_lookback=48,
            n_results=5,
            ticker=ticker # Inject real-time data for this stock
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stocks/{ticker}/details")
def get_stock_details_endpoint(ticker: str):
    try:
        data = fetch_stock_details(ticker)
        if not data:
             raise HTTPException(status_code=404, detail="Stock details not found")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
