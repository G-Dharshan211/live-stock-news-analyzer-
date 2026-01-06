// API Configuration
const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// ===============================
// Ticker-based Stock API
// ===============================
export async function fetchStockData(ticker) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/stocks/${ticker.toUpperCase()}`
    );

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Failed to fetch data for ${ticker}:`, error);

    // Fallback response
    return {
      answer: `Unable to retrieve real-time data for ${ticker.toUpperCase()}. Please try again later.`,
      sentiment: "Mixed",
      confidence: "Low",
      evidence: [],
      news: [],
    };
  }
}

export async function fetchStockDetails(ticker) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/stocks/${ticker}/details`);
    if (!response.ok) throw new Error('Failed to fetch details');
    return await response.json();
  } catch (error) {
    console.error("Failed to fetch stock details:", error);
    return null;
  }
}

// ===============================
// Watchlist API
// ===============================
export async function fetchWatchlist() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/watchlist`);

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    const tickers = await response.json();

    return tickers.map((ticker) => ({
      ticker,
      sentiment: "Mixed", // placeholder
    }));
  } catch (error) {
    console.error("Failed to fetch watchlist:", error);

    return [
      { ticker: "NVDA", sentiment: "Mixed" },
      { ticker: "AAPL", sentiment: "Mixed" },
      { ticker: "GOOGL", sentiment: "Mixed" },
    ];
  }
}

export async function addToWatchlist(ticker) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/watchlist/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker })
    });
    if (!response.ok) throw new Error('Failed to add stock');
    const list = await response.json();
    return list.map(t => ({ ticker: t, sentiment: "Mixed" }));
  } catch (error) {
    console.error("Failed to add to watchlist:", error);
    throw error;
  }
}

export async function removeFromWatchlist(ticker) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/watchlist/remove`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker })
    });
    if (!response.ok) throw new Error('Failed to remove stock');
    const list = await response.json();
    return list.map(t => ({ ticker: t, sentiment: "Mixed" }));
  } catch (error) {
    console.error("Failed to remove from watchlist:", error);
    throw error;
  }
}

// ===============================
// 🔥 RAG Question API (IMPORTANT)
// ===============================
export async function askQuestion(question) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      throw new Error(`Query failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to query RAG:", error);
    throw error;
  }
}

// ===============================
// Ingestion API
// ===============================
export async function triggerIngestion(ticker) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ingest`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ticker: ticker.toUpperCase() }),
    });

    if (!response.ok) {
      throw new Error(`Ingestion failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Ingestion failed for ${ticker}:`, error);
    throw error;
  }
}

// ===============================
// Health Check
// ===============================
export async function healthCheck() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    return response.ok;
  } catch (error) {
    console.error("Health check failed:", error);
    return false;
  }
}
