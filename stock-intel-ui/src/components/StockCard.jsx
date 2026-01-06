import React from 'react';
import { TrendingUp, TrendingDown, Minus, Clock } from 'lucide-react';
import { cn } from '../lib/utils';

const SENTIMENT_CONFIG = {
    Positive: { color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', icon: TrendingUp },
    Mixed: { color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20', icon: Minus },
    Negative: { color: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/20', icon: TrendingDown },
    Neutral: { color: 'text-slate-400', bg: 'bg-slate-500/10', border: 'border-slate-500/20', icon: Minus },
};

function formatTimeAgo(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return date.toLocaleDateString();
}

export default function StockCard({ ticker, data, onViewDetails }) {
    if (!data) {
        return (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                <div className="font-mono font-bold text-lg text-slate-100 mb-4">{ticker}</div>
                <div className="text-slate-500 text-sm">Loading...</div>
            </div>
        );
    }

    const config = SENTIMENT_CONFIG[data.sentiment] ?? SENTIMENT_CONFIG.Neutral;
    const Icon = config.icon;
    const recentNews = data.news?.slice(0, 3) || [];

    return (
        <div
            className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-slate-700 transition-all group cursor-pointer"
            onClick={() => onViewDetails && onViewDetails(ticker)}
        >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
                <div>
                    <h3 className="font-mono font-bold text-lg text-slate-100">{ticker}</h3>
                    <p className="text-xs text-slate-500">Click for details</p>
                </div>
                <div className={cn('flex items-center gap-1.5 px-2 py-1 rounded-lg border', config.bg, config.border)}>
                    <Icon className={cn('w-4 h-4', config.color)} />
                    <span className={cn('text-xs font-bold', config.color)}>{data.sentiment}</span>
                </div>
            </div>

            {/* Summary */}
            <div className="mb-4">
                <p className="text-sm text-slate-300 line-clamp-2">
                    {data.answer}
                </p>
            </div>

            {/* Recent News */}
            <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Recent News</h4>
                {recentNews.length > 0 ? (
                    <div className="space-y-2">
                        {recentNews.map((item, idx) => (
                            <div key={idx} className="border-l-2 border-slate-800 pl-3">
                                <p className="text-xs text-slate-400 line-clamp-1">{item.title}</p>
                                <div className="flex items-center gap-2 text-xs text-slate-600 mt-0.5">
                                    <span>{item.source}</span>
                                    <span>•</span>
                                    <span className="flex items-center gap-1">
                                        <Clock className="w-3 h-3" />
                                        {formatTimeAgo(item.timestamp)}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-xs text-slate-600 italic">No recent news</p>
                )}
            </div>

            {/* Confidence Badge */}
            <div className="mt-4 pt-4 border-t border-slate-800">
                <span className={cn(
                    'text-xs px-2 py-1 rounded border',
                    data.confidence === 'High'
                        ? 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400'
                        : data.confidence === 'Medium'
                            ? 'bg-slate-500/10 border-slate-500/20 text-slate-400'
                            : 'bg-rose-500/10 border-rose-500/20 text-rose-400'
                )}>
                    Confidence: {data.confidence}
                </span>
            </div>
        </div>
    );
}
