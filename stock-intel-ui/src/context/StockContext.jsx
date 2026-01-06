import React, { createContext, useContext, useState, useEffect } from "react";
import { fetchStockData, fetchWatchlist, askQuestion, fetchStockDetails } from "../lib/api";

const StockContext = createContext(undefined);

export function StockProvider({ children }) {
  // ─── State ─────────────────────────────────────────────
  const [currentTicker, setCurrentTicker] = useState(null);
  const [stockData, setStockData] = useState(null); // ticker-based
  const [stockDetails, setStockDetails] = useState(null);
  const [ragData, setRagData] = useState(null);     // question-based
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // ─── Actions ───────────────────────────────────────────
  const searchStock = async (ticker) => {
    setLoading(true);
    setError(null);
    setCurrentTicker(ticker);
    setRagData(null); // clear question result

    try {
      const result = await fetchStockData(ticker);
      setStockData(result);

      const details = await fetchStockDetails(ticker);
      setStockDetails(details);

      setLastUpdated(new Date());
    } catch (err) {
      setError("Failed to fetch stock data");
      setStockData(null);
      setStockDetails(null);
    } finally {
      setLoading(false);
    }
  };

  const queryRAG = async (question) => {
    console.log("STEP 3: queryRAG entered", question);
    setLoading(true);
    setError(null);
    setStockData(null); // clear ticker-based result
    setStockDetails(null);
    setCurrentTicker(null); // clear ticker

    try {
      const result = await askQuestion(question);
      console.log("STEP 3 RESULT:", result);
      setRagData(result);
      setLastUpdated(new Date());
    } catch (err) {
      console.error("STEP 3 ERROR:", err);
      setError("Failed to process question");
      setRagData(null);
    } finally {
      setLoading(false);
    }
  };

  // ─── Initial Load ──────────────────────────────────────
  useEffect(() => {
    const init = async () => {
      const list = await fetchWatchlist();
      setWatchlist(list);

      const initialTicker = list.length > 0 ? list[0].ticker : "NVDA";
      searchStock(initialTicker);
    };

    init();
  }, []);

  // ─── Context Value ─────────────────────────────────────
  const value = {
    // data
    currentTicker,
    stockData,
    stockDetails,
    ragData,
    watchlist,
    lastUpdated,

    // ui
    loading,
    error,

    // actions
    searchStock,
    queryRAG,
    setWatchlist,
  };

  return (
    <StockContext.Provider value={value}>
      {children}
    </StockContext.Provider>
  );
}

// ─── Hook ────────────────────────────────────────────────
export function useStock() {
  const context = useContext(StockContext);
  if (!context) {
    throw new Error("useStock must be used within StockProvider");
  }
  return context;
}
