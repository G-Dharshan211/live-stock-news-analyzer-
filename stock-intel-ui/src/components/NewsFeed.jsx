import React from 'react';
import { Newspaper, Clock } from 'lucide-react';
import { cn } from '../lib/utils';

function formatTimeAgo(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return date.toLocaleDateString();
}

export default function NewsFeed({ items }) {
    if (!items || items.length === 0) return null;

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full flex flex-col">
            <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-slate-100 flex items-center gap-2">
                    <Newspaper className="w-5 h-5 text-slate-400" />
                    Live News
                </h3>
                <span className="flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
            </div>

            <div className="flex-1 overflow-y-auto pr-2 space-y-4 custom-scrollbar">
                {items.map((item, index) => (
                    <a
                        key={index}
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block group cursor-pointer"
                    >
                        <div className="flex items-center gap-2 text-xs text-slate-500 mb-1">
                            <span className="font-mono text-emerald-500/80 font-medium">{item.source}</span>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {formatTimeAgo(item.timestamp)}
                            </span>
                        </div>
                        <h4 className="text-sm font-medium text-slate-300 group-hover:text-emerald-400 transition-colors leading-snug">
                            {item.title}
                        </h4>
                        <div className="w-full h-px bg-slate-800/50 mt-3 group-last:hidden" />
                    </a>
                ))}

                {/* Placeholder for "load more" or infinite scroll looks */}
                <div className="pt-2 text-center">
                    <div className="text-xs text-slate-600 italic">Streaming updates...</div>
                </div>
            </div>
        </div>
    );
}
