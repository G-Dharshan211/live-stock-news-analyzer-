"""
Direct test of query functions (no API server needed)
Tests the symbol filtering functionality directly
"""

from query import answer_user_query_json
from langchain_groq import ChatGroq

print("=" * 70)
print("🧪 DIRECT QUERY FUNCTION TEST (No API Server Needed)")
print("=" * 70)

# Test 1: Without symbol filter
print("\n" + "=" * 70)
print("TEST 1: Query WITHOUT symbol filter")
print("=" * 70)
print("Query: 'recent market performance'")
print("Symbol: None (searches all stocks)")

"""try:
    result1 = answer_user_query_json(
        query="recent market performance",
        hours_lookback=120,
        n_results=5,
    )
    
    print("\n✅ SUCCESS!")
    print(f"Answer: {result1['answer'][:200]}...")
    print(f"Sentiment: {result1['sentiment']}")
    print(f"Confidence: {result1['confidence']}")
    print(f"Evidence items: {len(result1['evidence'])}")
    print(f"News items: {len(result1['news'])}")
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()"""

# Test 2: With stock name in query (ITC)
print("\n" + "=" * 70)
print("TEST 2: Query with stock name in natural language")
print("=" * 70)
print("Query: 'how is ITC stock performing'")

try:
    result2 = answer_user_query_json(
        query="how is KTKBANK stock performing",
        hours_lookback=120,
        n_results=5
    )
    
    print("\n✅ SUCCESS!")
    print(f"Answer: {result2['answer'][:200]}...")
    print(f"Sentiment: {result2['sentiment']}")
    print(f"Confidence: {result2['confidence']}")
    print(f"Evidence items: {len(result2['evidence'])}")
    print(f"News items: {len(result2['news'])}")
    
    # Show evidence
    if result2['evidence']:
        print("\n📰 Evidence:")
        for i, ev in enumerate(result2['evidence'][:3]):
            print(f"  {i+1}. {ev['summary'][:80]}...")
            
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Different stocks in natural language
print("\n" + "=" * 70)
print("TEST 3: Testing multiple stocks with natural language queries")
print("=" * 70)

test_queries = [
    "how is ITC performing",
    "what is the recent performance of KTKBANK",
    "NATIONALUM stock analysis"
]

for query in test_queries:
    print(f"\n🔍 Testing: '{query}'")
    try:
        result = answer_user_query_json(
            query=query,
            hours_lookback=120,
            n_results=3
        )
        print(f"  ✅ {len(result['evidence'])} evidence items, sentiment: {result['sentiment']}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ All tests complete!")
print("=" * 70)
