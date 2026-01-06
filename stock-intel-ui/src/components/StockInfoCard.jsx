import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, Activity, PieChart, BarChart2 } from 'lucide-react';

export default function StockInfoCard({ details }) {
    if (!details) return null;

    const {
        price,
        change,
        change_percent,
        high,
        low,
        volume,
        pe_ratio,
        roe,
        profit_margin,
        market_cap,
        currency
    } = details;

    const isPositive = change >= 0;
    const currencySymbol = currency === 'INR' ? '₹' : '$';

    const formatNumber = (num) => {
        if (num === undefined || num === null) return '-';
        return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(num);
    };

    const formatLargeNumber = (num) => {
        if (!num) return '-';
        if (num >= 1.0e+12) return (num / 1.0e+12).toFixed(2) + "T";
        if (num >= 1.0e+9) return (num / 1.0e+9).toFixed(2) + "B";
        if (num >= 1.0e+6) return (num / 1.0e+6).toFixed(2) + "M";
        return formatNumber(num);
    };

    const formatPercent = (num) => {
        if (num === undefined || num === null) return '-';
        return (num * 100).toFixed(2) + '%';
    };

    // Metric Item Component
    const MetricItem = ({ label, value, subValue, icon: Icon, color = "text-slate-400" }) => (
        <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/50 flex flex-col gap-1">
            <div className="flex items-center gap-2 text-xs text-slate-500 font-medium uppercase tracking-wider">
                {Icon && <Icon className="w-3 h-3" />}
                {label}
            </div>
            <div className={`text-lg font-semibold ${color}`}>
                {value}
            </div>
            {subValue && <div className="text-xs text-slate-500">{subValue}</div>}
        </div>
    );

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg mb-6">
            {/* Header Section */}
            <div className="flex items-end justify-between mb-4 pb-4 border-b border-slate-800">
                <div>
                    <h2 className="text-sm font-medium text-slate-400">Current Price</h2>
                    <div className="flex items-baseline gap-3">
                        <span className="text-4xl font-bold text-white">
                            {currencySymbol}{formatNumber(price)}
                        </span>
                        <span className={`flex items-center text-sm font-medium px-2 py-0.5 rounded ${isPositive ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                            {isPositive ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                            {formatNumber(change)} ({formatNumber(change_percent)}%)
                        </span>
                    </div>
                </div>
                <div className="text-right hidden sm:block">
                    <div className="text-xs text-slate-500">Market Cap</div>
                    <div className="text-lg font-medium text-slate-300">{formatLargeNumber(market_cap)}</div>
                </div>
            </div>

            {/* Grid Layout */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <MetricItem
                    label="Day Range"
                    value={<div><span className="text-xs text-slate-500">L:</span> {formatNumber(low)} <span className="text-slate-600">|</span> <span className="text-xs text-slate-500">H:</span> {formatNumber(high)}</div>}
                    icon={Activity}
                    color="text-slate-200"
                />
                <MetricItem
                    label="Volume"
                    value={formatLargeNumber(volume)}
                    icon={BarChart2}
                    color="text-blue-400"
                />
                <MetricItem
                    label="P/E Ratio"
                    value={formatNumber(pe_ratio)}
                    icon={PieChart}
                    color="text-purple-400"
                />
                <MetricItem
                    label="ROE"
                    value={formatPercent(roe)}
                    icon={TrendingUp} // Or another relevant icon
                    color="text-amber-400"
                />
                {/* Optional: Add Profit Margin if space allows or replace one */}
                {/* <MetricItem label="Margin" value={formatPercent(profit_margin)} /> */}
            </div>
        </div>
    );
}
