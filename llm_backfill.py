from vector_store import get_collection
from llm_summarizer import summarize_from_headline
from langchain_groq import ChatGroq

def backfill_llm_summaries(limit=5):
    collection = get_collection()
    llm=ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    results = collection.get(
        where={"summary_source": "needs_llm"},
        limit=limit
    )

    ids = results["ids"]
    docs = results["documents"]
    metas = results["metadatas"]

    if not ids:
        print("✅ No documents need LLM summarization.")
        return

    for doc_id, doc, meta in zip(ids, docs, metas):
        title_line = [l for l in doc.splitlines() if l.startswith("Title:")]
        title = title_line[0].replace("Title:", "").strip()

        #print(f"🧠 Headline summarization: {title}")

        summary = summarize_from_headline(
            llm=llm,
            title=title,
            publisher=meta.get("publisher", "Unknown"),
            date=meta.get("date", "")
        )
        #print("LLM SUMMARY in llm_backfill:", summary)

        if not summary:
            print("⚠️ Empty LLM summary")
            continue

        new_text = f"""
Stock: {meta.get('symbol', meta.get('ticker', 'UNKNOWN'))}
Title: {title}
Summary: {summary}
""".strip()

        meta["summary_source"] = "llm_headline"

        collection.upsert(
            ids=[doc_id],
            documents=[new_text],
            metadatas=[meta]
        )

        print("✅ Headline summary stored")
