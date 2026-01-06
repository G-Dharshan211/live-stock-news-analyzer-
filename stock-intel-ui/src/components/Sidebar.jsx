import React, { useState } from 'react';
import { useStock } from '../context/StockContext';
import { cn } from '../lib/utils';
import { TrendingUp, Activity, Plus, X, Trash2 } from 'lucide-react';
import { addToWatchlist, removeFromWatchlist } from '../lib/api';

const SENTIMENT_COLORS = {
    Positive: "bg-emerald-500",
    Mixed: "bg-amber-500",
    Negative: "bg-rose-500",
    Neutral: "bg-slate-500"
};

export default function Sidebar() {
    const { watchlist, currentTicker, searchStock, setWatchlist } = useStock();
    const [newTicker, setNewTicker] = useState("");
    const [isAdding, setIsAdding] = useState(false);

    const handleAddStock = async (e) => {
        e.preventDefault();
        if (!newTicker.trim()) return;

        setIsAdding(true);
        try {
            const updatedList = await addToWatchlist(newTicker);
            setWatchlist(updatedList);
            setNewTicker("");
        } catch (err) {
            console.error(err);
        } finally {
            setIsAdding(false);
        }
    };

    const handleRemoveStock = async (ticker, e) => {
        e.stopPropagation(); // prevent clicking the stock
        if (window.confirm(`Remove ${ticker} from watchlist?`)) {
            try {
                const updatedList = await removeFromWatchlist(ticker);
                setWatchlist(updatedList);
            } catch (err) {
                console.error(err);
            }
        }
    };

    return (
        <div className="w-64 bg-slate-900 border-r border-slate-800 h-screen flex flex-col fixed left-0 top-0 z-10">
            <div className="p-6 border-b border-slate-800 flex items-center gap-2">
                <Activity className="text-emerald-400 w-6 h-6" />
                <span className="text-lg font-bold text-slate-100 tracking-tight">StockIntel</span>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 px-2">
                    Watchlist
                </h3>

                <div className="space-y-1">
                    {watchlist.map((stock) => (
                        <div key={stock.ticker} className="relative group">
                            <button
                                onClick={() => searchStock(stock.ticker)}
                                className={cn(
                                    "w-full flex items-center justify-between p-2 rounded-lg transition-all duration-200 group text-left",
                                    currentTicker === stock.ticker
                                        ? "bg-slate-800 text-white shadow-sm ring-1 ring-slate-700"
                                        : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                                )}
                            >
                                <span className="font-medium font-mono">{stock.ticker}</span>
                                <div
                                    className={cn("w-2 h-2 rounded-full ring-2 ring-slate-900", SENTIMENT_COLORS[stock.sentiment])}
                                    title={stock.sentiment}
                                />
                            </button>
                            <button
                                onClick={(e) => handleRemoveStock(stock.ticker, e)}
                                className="absolute right-8 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 p-1 hover:bg-rose-500/20 rounded text-rose-500 transition-all"
                                title="Remove"
                            >
                                <X className="w-3 h-3" />
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Add Stock Input */}
            <div className="p-4 border-t border-slate-800 bg-slate-900">
                <form onSubmit={handleAddStock} className="flex gap-2">
                    <input
                        type="text"
                        value={newTicker}
                        onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
                        placeholder="Add ticker..."
                        className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-emerald-500"
                        maxLength={15}
                    />
                    <button
                        type="submit"
                        disabled={isAdding || !newTicker}
                        className="bg-emerald-600 hover:bg-emerald-500 text-white rounded p-1 disabled:opacity-50"
                    >
                        <Plus className="w-5 h-5" />
                    </button>
                </form>
            </div>

            <div className="p-4 border-t border-slate-800">
                <div className="bg-slate-800/50 rounded-lg p-3 text-xs text-slate-400">
                    <p className="flex items-center gap-1.5 mb-1 text-emerald-400">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                        System Live
                    </p>
                    <p>Index ingestion active</p>
                </div>
            </div>
        </div>
    );
}
