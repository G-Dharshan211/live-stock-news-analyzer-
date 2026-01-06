import React from "react";
import { cn } from "../lib/utils";
import EvidenceList from "./EvidenceList";
import { Sparkles, TrendingUp, TrendingDown, Minus } from "lucide-react";


const SENTIMENT_CONFIG = {
    Positive: { color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20", icon: TrendingUp },
    Mixed: { color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20", icon: Minus },
    Negative: { color: "text-rose-400", bg: "bg-rose-500/10", border: "border-rose-500/20", icon: TrendingDown },
    Neutral: { color: "text-slate-400", bg: "bg-slate-500/10", border: "border-slate-500/20", icon: Minus },
};

export default function AnswerCard({ ticker, data }) {
    if (!data) return null;

    const config = SENTIMENT_CONFIG[data.sentiment] ?? SENTIMENT_CONFIG.Neutral;
    const Icon = config.icon;

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl shadow-black/20 backdrop-blur-sm relative overflow-hidden group">
            {/* Decorative gradient blob */}
            <div
                className={cn(
                    "absolute top-0 right-0 w-64 h-64 rounded-full blur-3xl opacity-10 pointer-events-none -translate-y-1/2 translate-x-1/2",
                    config.bg.replace("/10", "/30")
                )}
            />

            <div className="flex items-start justify-between mb-6 relative">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-slate-800 rounded-lg border border-slate-700">
                        <Sparkles className="w-5 h-5 text-indigo-400" />
                    </div>

                    <div>
                        <h2 className="text-xl font-bold text-slate-100 tracking-tight">
                            AI Analysis{ticker ? `: ${ticker}` : ""}
                        </h2>

                        <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
                            <span>Confidence:</span>
                            <span
                                className={cn(
                                    "px-1.5 py-0.5 rounded font-medium border",
                                    data.confidence === "High"
                                        ? "bg-indigo-500/10 border-indigo-500/20 text-indigo-400"
                                        : data.confidence === "Medium"
                                            ? "bg-slate-500/10 border-slate-500/20 text-slate-400"
                                            : "bg-rose-500/10 border-rose-500/20 text-rose-400"
                                )}
                            >
                                {data.confidence}
                            </span>
                        </div>
                    </div>
                </div>

                <div className={cn("flex flex-col items-end px-3 py-1.5 rounded-lg border", config.bg, config.border)}>
                    <div className="flex items-center gap-1.5">
                        <span className={cn("text-xs font-bold uppercase tracking-wider", config.color)}>
                            {data.sentiment}
                        </span>
                        <Icon className={cn("w-4 h-4", config.color)} />
                    </div>
                </div>
            </div>

            <div className="prose prose-invert prose-p:text-slate-300 prose-p:leading-relaxed max-w-none relative">
                <p className="text-lg">{data.answer}</p>
            </div>

            <EvidenceList items={data.evidence} />
        </div>
    );
}
