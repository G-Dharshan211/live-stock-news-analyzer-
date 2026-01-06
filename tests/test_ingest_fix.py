from ingest_all import ingest_all
from llm_backfill import backfill_llm_summaries
from vector_store import get_collection
def inspect_summary_sources():
    """Check how many documents need LLM processing"""
    collection = get_collection()
    
    # Get all documents
    all_docs = collection.get()
    
    # Count by summary_source
    sources = {}
    for meta in all_docs['metadatas']:
        source = meta.get('summary_source', 'UNKNOWN')
        sources[source] = sources.get(source, 0) + 1
    
    print("\n📊 Summary Source Breakdown:")
    print("-" * 40)
    for source, count in sorted(sources.items()):
        print(f"  {source}: {count} documents")
    print("-" * 40)
    
    return sources

TICKER = ["KTKBANK"]
print("Starting ingestion test...")
for t in TICKER:
    try:
        ingest_all(t)
    except Exception as e:
        print(f"FAILED for {t}: {e}")
        raise e
print("Ingestion test complete!")
sources_before = inspect_summary_sources()
    
needs_llm_count = sources_before.get('needs_llm', 0)
print(f"\n🔍 Found {needs_llm_count} documents needing LLM processing")
    
if needs_llm_count == 0:
    print("\n✅ All summaries are already good quality!")
    print("   (This means RSS summaries passed quality check)")
else:
    # Step 3: Run backfill
    print(f"\n🧠 Step 3: Running LLM backfill for up to {needs_llm_count} documents...")
    try:
        backfill_llm_summaries(limit=needs_llm_count)
    except Exception as e:
        print(f"❌ Backfill failed: {e}")
        import traceback
        traceback.print_exc()
        
    # Step 4: Check results
    print("\n📊 Step 4: Checking results...")
    sources_after = inspect_summary_sources()
    
    llm_headline_count = sources_after.get('llm_headline', 0)
    remaining_needs_llm = sources_after.get('needs_llm', 0)
        
    print(f"\n✅ Results:")
    print(f"  - Processed: {llm_headline_count} documents")
    print(f"  - Remaining: {remaining_needs_llm} documents")
    
    print("\n" + "=" * 60)
    print("🎉 TEST COMPLETE")
    print("=" * 60)
