"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import TransactionTable from "@/components/TransactionTable";
import EnvelopeGrid from "@/components/EnvelopeGrid";
import MarketTicker from "@/components/MarketTicker";
import NewTransactionModal from "@/components/NewTransactionModal";
import { api, type EnvelopeDTO } from "@/lib/api";
import { Settings2, LogOut, Plus, Wallet, Banknote } from "lucide-react";

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

  const allocatedTotal = envelopes.reduce(
    (sum, e) => sum + parseFloat(e.current_balance), 0,
  );
  const unallocated = netBalance !== null ? netBalance - allocatedTotal : null;

  return (
    <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">FinanceMacro</h1>
          <p className="mt-1 text-sm text-slate-400">
            Passive financial manager — share a receipt to log it.
          </p>
        </div>
        <nav className="flex items-center gap-3">
          <button
            onClick={() => setShowNewTx(true)}
            className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-2 text-xs font-medium text-white transition hover:bg-indigo-500"
          >
            <Plus size={14} /> New Transaction
          </button>
          <Link
            href="/rules"
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 px-3 py-2 text-xs font-medium text-slate-300 transition hover:bg-slate-800"
          >
            <Settings2 size={14} /> Rules
          </Link>
          <Link
            href="/login"
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 px-3 py-2 text-xs font-medium text-slate-300 transition hover:bg-slate-800"
          >
            <LogOut size={14} /> Login
          </Link>
        </nav>
      </div>

      {/* Stats row */}
      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Wallet size={16} className="text-indigo-400" />
            Net Balance
          </div>
          <p className="mt-1 text-xl font-bold tabular-nums text-slate-100">
            {netBalance !== null ? `$${netBalance.toFixed(2)}` : "—"}
          </p>
        </div>

        <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Banknote size={16} className="text-emerald-400" />
            In Envelopes
          </div>
          <p className="mt-1 text-xl font-bold tabular-nums text-slate-100">
            ${allocatedTotal.toFixed(2)}
          </p>
        </div>

        <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Wallet size={16} className={unallocated !== null && unallocated > 0 ? "text-amber-400" : "text-slate-500"} />
            Unallocated
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
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-400">
              Netting Status
            </h3>
            <p className="text-sm text-slate-500">
              Large expenses auto-enter netting mode. Incoming transfers within 12h are absorbed — they never distort your income chart.
            </p>
          </div>
        </div>
      </div>

      {showNewTx && (
        <NewTransactionModal
          onClose={() => setShowNewTx(false)}
          onDone={() => {
            setShowNewTx(false);
            loadFunds();
          }}
        />
      )}
    </div>
  );
}
