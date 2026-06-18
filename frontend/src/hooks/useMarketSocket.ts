"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export interface MarketTick {
  symbol: string;
  price: number;
  change: number;
  timestamp: string;
}

export function useMarketSocket() {
  const [ticks, setTicks] = useState<Map<string, MarketTick>>(new Map());
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api/v1/market/ws";
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (e) => {
      try {
        const tick: MarketTick = JSON.parse(e.data);
        setTicks((prev) => {
          const next = new Map(prev);
          next.set(tick.symbol, tick);
          return next;
        });
      } catch { /* silent */ }
    };
    ws.onerror = () => setConnected(false);
  }, []);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { ticks, connected };
}
