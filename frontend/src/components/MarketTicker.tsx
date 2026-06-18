"use client";

import { useMarketSocket, type MarketTick } from "@/hooks/useMarketSocket";
import { TrendingUp, TrendingDown, Wifi, WifiOff } from "lucide-react";

function TickerRow({ tick }: { tick: MarketTick }) {
  const isUp = tick.change >= 0;
  return (
    <div className="flex items-center justify-between gap-4 rounded-lg bg-slate-800/60 px-4 py-3 text-sm">
      <span className="font-medium text-slate-200">{tick.symbol}</span>
      <span className="font-mono tabular-nums text-slate-100">
        ${tick.price.toFixed(2)}
      </span>
      <span
        className={`flex items-center gap-1 font-mono tabular-nums ${isUp ? "text-emerald-400" : "text-red-400"}`}
      >
        {isUp ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
        {isUp ? "+" : ""}
        {tick.change.toFixed(2)}%
      </span>
    </div>
  );
}

export default function MarketTicker() {
  const { ticks, connected } = useMarketSocket();
  const values = Array.from(ticks.values());

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-100">Live Quotes</h2>
        {connected ? (
          <span className="flex items-center gap-1.5 text-xs text-emerald-400">
            <Wifi size={14} /> Live
          </span>
        ) : (
          <span className="flex items-center gap-1.5 text-xs text-slate-500">
            <WifiOff size={14} /> Disconnected
          </span>
        )}
      </div>
      <div className="space-y-2">
        {!values.length && (
          <p className="py-4 text-center text-sm text-slate-500">
            {connected ? "Waiting for ticks..." : "Connecting..."}
          </p>
        )}
        {values.map((t) => (
          <TickerRow key={t.symbol} tick={t} />
        ))}
      </div>
    </div>
  );
}
