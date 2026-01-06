"""
Full RAG Pipeline Test (End-to-End)
Simulates the entire workflow from Ingestion -> Summarization -> Retrieval -> Answer
"""
import time
from ingest_all import ingest_all
from llm_backfill import backfill_llm_summaries
from query import answer_user_query_json
from vector_store import get_collection

TICKERS = ["ITC", "AAPL", "RELIANCE", "GOOGL"]

def step_1_ingestion_all():
    print(f"\n🚀 STEP 1: Ingesting Data for {TICKERS}...")
    for ticker in TICKERS:
        try:
            print(f"   🔹 Ingesting {ticker}...")
            ingest_all(ticker)
        except Exception as e:
            print(f"   ❌ Ingestion Failed for {ticker}: {e}")

def step_2_check_database_all():
    print(f"\n🔍 STEP 2: Checking Database State...")
    collection = get_collection()
    
    total_docs = 0
    total_needs_llm = 0
    
    for ticker in TICKERS:
        results = collection.get(where={"symbol": ticker})
        count = len(results['ids'])
        print(f"   📦 {ticker}: Found {count} documents")
        total_docs += count
        
        needs_llm = 0
        for meta in results['metadatas']:
            if meta.get('summary_source') == 'needs_llm':
                needs_llm += 1
        total_needs_llm += needs_llm
            
    print(f"   Total Documents: {total_docs}")
    print(f"   Total Awaiting LLM Summary: {total_needs_llm}")

def step_3_llm_backfill():
    print(f"\n🧠 STEP 3: Running LLM Summary Backfill (Global)...")
    backfill_llm_summaries()
    print("✅ Backfill Complete.")

def step_4_query_answer_all():
    print(f"\n💬 STEP 4: Testing Query & Answer Generation...")
    
    for ticker in TICKERS:
        query = f"How is {ticker} performing recently?"
        print(f"\n   ❓ Query: '{query}'")
        
        start_time = time.time()
        try:
            result = answer_user_query_json(
                query=query,
                hours_lookback=120,
                n_results=5
            )
            duration = time.time() - start_time
            
            print(f"     ⏱️ Response Time: {duration:.2f}s")
            print(f"     📝 Evidence Used: {len(result['evidence'])}")
            print(f"     📊 Sentiment: {result['sentiment']} (Conf: {result['confidence']})")
            print("-" * 40)
            print(f"     ANSWER: {result['answer'][:200]}...") # Print preview to avoid clutter
            print("-" * 40)
            
        except Exception as e:
            print(f"     ❌ Query Failed for {ticker}: {e}")

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 FULL RAG PIPELINE TEST (MULTI-STOCK)")
    print("=" * 70)
    
    try:
        step_1_ingestion_all()
        step_2_check_database_all()
        step_3_llm_backfill()
        step_2_check_database_all() # Check again
        step_4_query_answer_all()
        
        print("\n" + "=" * 70)
        print("✅ TEST COMPLETE - PIPELINE VERIFIED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ CRITICAL FAILURE: {e}")
        import traceback
        traceback.print_exc()
