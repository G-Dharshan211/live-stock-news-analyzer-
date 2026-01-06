# Traders Paradise 📈

Traders Paradise is an intelligent stock analysis platform that combines real-time data ingestion, semantic search (RAG), and LLM-based reasoning to provide actionable financial insights.

## 🌟 Key Features

### 🧠 Advanced RAG Engine
*   **Semantic Search**: Query in plain English (e.g., "Why is Gold rising?"). The system automatically identifies the asset and intent.
*   **Multi-Source Ingestion**:
    *   **Google News**: Global context and qualitative analysis.
    *   **AlphaVantage**: Financial sentiment scores and market data.
    *   **MoneyControl**: Deep coverage for Indian markets (via RSS proxy).
*   **Qualitative Reasoning**: Explains the *cause* of price movements (e.g., inflation, war) rather than just reporting the numbers.

### ⚡ Real-Time Intelligence
*   **Live News Feed**: Sidebar featuring the top 5 most relevant news items.
*   **Source Transparency**: Every data point includes a direct, clickable link to the original article.
*   **Time-Aware**: Filters analysis to the last **120 hours (5 days)** by default.

---

## 🛠️ Installation

1.  **Clone the repository**
2.  **Install Python Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Environment Variables**
    Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=your_key_here
    ALPHAVANTAGE_API_KEY=your_key_here
    ```

---

## 🚀 Usage

### 1. Start the Backend API
The FastAPI server handles data ingestion, vector storage, and query resolution.
```bash
python -m uvicorn api:app --reload --port 8000
```
*   **API**: `http://localhost:8000`
*   **Docs**: `http://localhost:8000/docs`

### 2. Start the Frontend Dashboard
The React-based UI visualizes the analysis.
```bash
cd ../stock-intel-ui
npm run dev
```
*   **UI**: `http://localhost:5173`

---

## 📡 API Reference

### Analyze a Stock
**Endpoint**: `POST /api/query`

**Payload**:
```json
{
  "question": "How is ITC performing?",
  "hours_lookback": 120
}
```

**Response**:
```json
{
  "answer": "ITC has seen steady growth due to...",
  "sentiment": "Positive",
  "confidence": "High",
  "news": [
    {
      "title": "ITC Q3 Results...",
      "url": "https://www.moneycontrol.com/...",
      "source": "MoneyControl"
    }
  ]
}
```

Note: The `hours_lookback` parameter defaults to 120 if omitted.

---

## 🧪 Verification & Testing

Run these scripts to verify system health:

| Script | description |
|--------|-------------|
| `test_full_rag_flow.py` | Master Test: Runs Ingestion -> Backfill -> Query -> Answer for multiple stocks (ITC, AAPL, etc.). |
| `test_query_direct.py` | Tests direct query to LLM. |
| `test_ingest_all.py ` | Tests ingestion of all sources. |
| `test_moneycontrol.py` | Verifies specific ingestion from MoneyControl for Indian stocks. |

---

📂 Project Structure

`api.py`: FastAPI application entry point.
`ingest_all.py`: Orchestrator for multi-source ingestion.
`query.py`: Core RAG logic (Retrieval, Fusion, Answer Generation).
`ingestion/`: Modules for individual sources (`google_news.py`, `moneycontrol.py`, `alphavantage_news.py`).
`stock-intel-ui/`: Frontend React application.
