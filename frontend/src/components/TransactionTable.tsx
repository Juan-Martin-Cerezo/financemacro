"use client";

import { useCallback, useEffect, useState } from "react";
import { api, type TransactionDTO } from "@/lib/api";
import { ArrowDownCircle, ArrowUpCircle, Loader2 } from "lucide-react";

function CategoryBadge({ cat }: { cat: TransactionDTO["category"] }) {
  if (!cat) return null;
  return (
    <span
      className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium"
      style={{ backgroundColor: cat.color + "20", color: cat.color }}
    >
      {cat.name}
    </span>
  );
}

export default function TransactionTable() {
  const [txs, setTxs] = useState<TransactionDTO[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try { setTxs(await api.transactions.list()); } catch { /* silent */ }
  }, []);

  useEffect(() => { load().finally(() => setLoading(false)); }, [load]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="animate-spin text-indigo-400" size={28} />
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900">
      <div className="border-b border-slate-700 px-5 py-3">
        <h2 className="text-lg font-semibold text-slate-100">Transactions</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-700 text-xs uppercase text-slate-400">
            <tr>
              <th className="px-5 py-3 font-medium">Date</th>
              <th className="px-5 py-3 font-medium">Description</th>
              <th className="px-5 py-3 font-medium">Category</th>
              <th className="px-5 py-3 font-medium text-right">Amount</th>
              <th className="px-5 py-3 font-medium text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            {!txs.length && (
              <tr>
                <td colSpan={5} className="px-5 py-12 text-center text-slate-500">
                  No transactions yet. Share a receipt to start.
                </td>
              </tr>
            )}
            {txs.map((tx) => (
              <tr key={tx.id} className="border-b border-slate-800 last:border-0 hover:bg-slate-800/40">
                <td className="px-5 py-3 font-mono text-xs text-slate-400">
                  {new Date(tx.transaction_date).toLocaleDateString()}
                </td>
                <td className="px-5 py-3 text-slate-200">{tx.description || "—"}</td>
                <td className="px-5 py-3"><CategoryBadge cat={tx.category} /></td>
                <td className={`flex items-center justify-end gap-1 px-5 py-3 font-mono tabular-nums ${tx.amount > 0 ? "text-emerald-400" : "text-red-400"}`}>
                  {tx.amount > 0 ? <ArrowUpCircle size={14} /> : <ArrowDownCircle size={14} />}
                  ${Math.abs(tx.amount).toFixed(2)}
                </td>
                <td className="px-5 py-3 text-center">
                  <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${
                    tx.status === "absorbed" ? "bg-slate-700 text-slate-400" :
                    tx.status === "pending_netting" ? "bg-amber-900/50 text-amber-300" :
                    "bg-emerald-900/50 text-emerald-300"
                  }`}>
                    {tx.status.replace("_", " ")}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
