"use client";

import { useState } from "react";
import { api, type EnvelopeDTO } from "@/lib/api";
import { Loader2, X, ArrowRightLeft } from "lucide-react";

export default function AllocateModal({
  envelope,
  onClose,
  onDone,
}: {
  envelope: EnvelopeDTO;
  onClose: () => void;
  onDone: () => void;
}) {
  const [amount, setAmount] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    const parsed = parseFloat(amount);
    if (!parsed || parsed <= 0) {
      setError("Enter a positive amount");
      return;
    }
    setSaving(true);
    try {
      await api.envelopes.allocate(envelope.id, parsed);
      onDone();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Allocation failed";
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4">
      <div className="w-full max-w-sm rounded-xl border border-slate-700 bg-slate-900 p-6">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ArrowRightLeft size={18} className="text-indigo-400" />
            <h2 className="text-lg font-semibold text-slate-100">Allocate Funds</h2>
          </div>
          <button
            onClick={onClose}
            className="rounded p-1 text-slate-500 transition hover:bg-slate-800 hover:text-slate-300"
          >
            <X size={18} />
          </button>
        </div>

        <p className="mb-4 text-sm text-slate-400">
          Add funds to <span className="font-medium text-slate-200">{envelope.name}</span>.
          Current balance: <span className="font-mono">${parseFloat(envelope.current_balance).toFixed(2)}</span>
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">Amount</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              required
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.00"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm font-mono text-slate-100 placeholder-slate-500 outline-none focus:border-indigo-500"
              autoFocus
            />
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:opacity-60"
            >
              {saving ? <Loader2 size={14} className="animate-spin" /> : null}
              {saving ? "Allocating..." : "Allocate"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
