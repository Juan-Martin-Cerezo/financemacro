"use client";

import { useCallback, useEffect, useState } from "react";
import TransactionTable from "@/components/TransactionTable";
import EnvelopeGrid from "@/components/EnvelopeGrid";
import MarketTicker from "@/components/MarketTicker";
import NewTransactionModal from "@/components/NewTransactionModal";
import { api, type EnvelopeDTO } from "@/lib/api";
import { Plus, Wallet, Banknote, AlertTriangle } from "lucide-react";

export default function Dashboard() {
  const [showNewTx, setShowNewTx] = useState(false);
  const [netBalance, setNetBalance] = useState<number | null>(null);
  const [envelopes, setEnvelopes] = useState<EnvelopeDTO[]>([]);

  const loadFunds = useCallback(async () => {
    try {
      const [bal, envs] = await Promise.all([
        api.transactions.netBalance(),
        api.envelopes.list(),
      ]);
      setNetBalance(parseFloat(bal.net_balance));
      setEnvelopes(envs);
    } catch { /* silent */ }
  }, []);

  useEffect(() => { loadFunds(); }, [loadFunds]);

  const allocatedTotal = envelopes.reduce((s, e) => s + parseFloat(e.current_balance), 0);
  const unallocated = netBalance !== null ? netBalance - allocatedTotal : null;

  const targetTotal = envelopes.reduce(
    (s, e) => s + (e.target_amount ? parseFloat(e.target_amount) : 0),
    0,
  );
  const deficit = netBalance !== null && targetTotal > 0 && netBalance < targetTotal;

  return (
    <div className="mx-auto max-w-6xl px-6 py-6">
      {/* Liquidity Watchdog banner */}
      {deficit && (
        <div className="mb-6 flex items-center gap-3 rounded-xl border border-red-800 bg-red-900/40 px-5 py-4">
          <AlertTriangle size={22} className="shrink-0 text-red-400" />
          <div>
            <p className="text-sm font-semibold text-red-200">Liquidity Deficit</p>
            <p className="text-xs text-red-300/80">
              Net balance (${netBalance!.toFixed(2)}) is below total envelope targets (${targetTotal.toFixed(2)}).
              Envelope commitments exceed available funds by ${(targetTotal - netBalance!).toFixed(2)}.
            </p>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Dashboard</h1>
          <p className="mt-1 text-sm text-slate-400">Share a receipt to log it automatically.</p>
        </div>
        <button
          onClick={() => setShowNewTx(true)}
          className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-2 text-xs font-medium text-white hover:bg-indigo-500"
        >
          <Plus size={14} /> New Transaction
        </button>
      </div>

      {/* Stats row */}
      <div className="mb-6 grid gap-4 sm:grid-cols-4">
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Wallet size={16} className="text-indigo-400" /> Net Balance
          </div>
          <p className="mt-1 text-xl font-bold tabular-nums text-slate-100">
            {netBalance !== null ? `$${netBalance.toFixed(2)}` : "—"}
          </p>
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Wallet size={16} className="text-amber-400" /> Target Total
          </div>
          <p className="mt-1 text-xl font-bold tabular-nums text-slate-100">
            ${targetTotal.toFixed(2)}
          </p>
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Banknote size={16} className="text-emerald-400" /> In Envelopes
          </div>
          <p className="mt-1 text-xl font-bold tabular-nums text-slate-100">
            ${allocatedTotal.toFixed(2)}
          </p>
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Wallet size={16} className={unallocated !== null && unallocated > 0 ? "text-amber-400" : "text-slate-500"} /> Unallocated
          </div>
          <p className={`mt-1 text-xl font-bold tabular-nums ${unallocated !== null && unallocated >= 0 ? "text-slate-100" : "text-red-400"}`}>
            {unallocated !== null ? `$${unallocated.toFixed(2)}` : "—"}
          </p>
        </div>
      </div>

      {/* Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <TransactionTable />
          <EnvelopeGrid />
        </div>
        <div className="space-y-6">
          <MarketTicker />
          <div className="rounded-xl border border-slate-700 bg-slate-900 p-5">
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-400">Netting Status</h3>
            <p className="text-sm text-slate-500">Large expenses auto-enter netting mode. Incoming transfers within 12h are absorbed — they never distort your income chart.</p>
          </div>
        </div>
      </div>

      {showNewTx && (
        <NewTransactionModal
          onClose={() => setShowNewTx(false)}
          onDone={() => { setShowNewTx(false); loadFunds(); }}
        />
      )}
    </div>
  );
}
