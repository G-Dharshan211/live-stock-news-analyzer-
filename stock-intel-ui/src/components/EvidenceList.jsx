import React from 'react';
import { ExternalLink, FileText } from 'lucide-react';

export default function EvidenceList({ items }) {
    if (!items || items.length === 0) return null;

    return (
        <div className="mt-6 border-t border-slate-800 pt-4">
            <h4 className="text-sm font-semibold text-slate-400 mb-3 flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Key Evidence & Sources
            </h4>
            <ul className="space-y-3">
                {items.map((item, index) => (
                    <li key={index} className="flex flex-col sm:flex-row sm:items-start gap-1 sm:gap-2 text-sm group">
                        <span className="text-slate-500 mt-1 sm:mt-0.5">•</span>
                        <div className="flex-1">
                            <span className="text-slate-300 leading-relaxed block sm:inline">{item.summary} </span>
                            {item.source_url && (
                                <a
                                    href={item.source_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-1 text-emerald-500 hover:text-emerald-400 font-medium whitespace-nowrap opacity-80 hover:opacity-100 transition-opacity ml-1"
                                >
                                    Source <ExternalLink className="w-3 h-3" />
                                </a>
                            )}
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
}
