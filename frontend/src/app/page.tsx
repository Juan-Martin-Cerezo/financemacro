import Link from "next/link";
import TransactionTable from "@/components/TransactionTable";
import EnvelopeGrid from "@/components/EnvelopeGrid";
import MarketTicker from "@/components/MarketTicker";
import { Settings2, LogOut } from "lucide-react";

export default function Dashboard() {
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
    </div>
  );
}
