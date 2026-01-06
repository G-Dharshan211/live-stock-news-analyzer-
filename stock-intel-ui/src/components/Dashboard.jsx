import React from 'react';
import { useStock } from '../context/StockContext';
import AnswerCard from './AnswerCard';
import StockInfoCard from './StockInfoCard';
import NewsFeed from './NewsFeed';
import { AlertCircle } from 'lucide-react';

export default function Dashboard() {
    const { currentTicker, stockData, stockDetails, ragData, loading } = useStock();

    // Prioritize RAG data (from search) over stock data (from ticker selection)
    const displayData = ragData || stockData;
    const displayTicker = ragData ? null : currentTicker; // Hide ticker label for RAG queries

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] text-slate-400 gap-4">
                <div className="w-12 h-12 border-4 border-slate-800 border-t-emerald-500 rounded-full animate-spin" />
                <p className="animate-pulse">Analyzing market signals{currentTicker ? ` for ` : ''}
                    {currentTicker && <span className="text-emerald-400 font-mono font-bold">{currentTicker}</span>}
                    ...
                </p>
            </div>
        );
    }

    if (!displayData) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] text-slate-500 gap-4">
                <div className="p-4 bg-slate-900 rounded-full border border-slate-800">
                    <AlertCircle className="w-8 h-8 opacity-50" />
                </div>
                <p>Select a stock or search to begin analysis</p>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
            {/* Main Content - 2 Columns */}
            <div className="lg:col-span-2 space-y-6">
                <StockInfoCard details={stockDetails} />
                <AnswerCard data={displayData} ticker={displayTicker} />
            </div>

            {/* Sidebar Content - 1 Column */}
            <div className="lg:col-span-1 h-full min-h-[500px]">
                <NewsFeed items={displayData.news} />
            </div>
        </div>
    );
}
