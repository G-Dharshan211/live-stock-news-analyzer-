import React, { useState } from "react";
import { useStock } from "../context/StockContext";
import { Search, Bell } from "lucide-react";

export default function TopBar() {
  const { lastUpdated, loading, queryRAG } = useStock();
  const [query, setQuery] = useState("");

const handleSubmit = (e) => {
  e.preventDefault();
  console.log("STEP 2: submit fired", query);
  queryRAG(query);
};

  return (
    <div className="h-16 bg-slate-900/50 backdrop-blur-md border-b border-slate-800 flex items-center px-6 sticky top-0 z-20 ml-64">
      
      {/* ✅ Search bar MUST be inside a form */}
      <form
        onSubmit={handleSubmit}
        className="flex-1 max-w-2xl relative"
      >
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />

        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about a stock (e.g. 'How is NVDA performing today?')"
          className="w-full bg-slate-950 border border-slate-800 rounded-full pl-10 pr-4 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 placeholder:text-slate-500 transition-all font-light"
        />

        {loading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="w-4 h-4 border-2 border-slate-600 border-t-emerald-500 rounded-full animate-spin" />
          </div>
        )}
      </form>

      {/* Right side */}
      <div className="flex items-center gap-4 ml-auto">
        <div className="text-right hidden md:block">
          <p className="text-xs text-slate-400 font-medium">Last Updated</p>
          <p className="text-xs text-slate-500 font-mono">
            {lastUpdated
              ? lastUpdated.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                  second: "2-digit",
                })
              : "—"}
          </p>
        </div>

        <button className="p-2 text-slate-400 hover:text-white transition-colors relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-emerald-500 rounded-full ring-2 ring-slate-900" />
        </button>
      </div>
    </div>
  );
}
