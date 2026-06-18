"use client";

import { useCallback, useEffect, useState } from "react";
import { api, type EnvelopeDTO } from "@/lib/api";
import { Loader2, PiggyBank, Wallet, Plus } from "lucide-react";
import AllocateModal from "./AllocateModal";

function EnvelopeCard({
  env,
  onAllocate,
}: {
  env: EnvelopeDTO;
  onAllocate: (e: EnvelopeDTO) => void;
}) {
  const target = env.target_amount ? parseFloat(env.target_amount) : null;
  const balance = parseFloat(env.current_balance);
  const pct = target && target > 0 ? Math.min((balance / target) * 100, 100) : 0;

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-4">
      <div className="mb-3 flex items-center gap-2">
        <PiggyBank size={18} className="text-indigo-400" />
        <h3 className="font-medium text-slate-100">{env.name}</h3>
      </div>
      <div className="mb-2 flex items-baseline justify-between">
        <span className="text-2xl font-bold tabular-nums text-slate-100">
          ${balance.toFixed(2)}
        </span>
        {target != null && (
          <span className="text-xs text-slate-400">of ${target.toFixed(2)}</span>
        )}
      </div>
      {target != null && (
        <div className="mb-3 h-2 w-full overflow-hidden rounded-full bg-slate-700">
          <div
            className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all"
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
      <button
        onClick={() => onAllocate(env)}
        className="mt-2 flex w-full items-center justify-center gap-1.5 rounded-lg border border-indigo-700/50 px-3 py-1.5 text-xs font-medium text-indigo-300 transition hover:bg-indigo-900/30 hover:text-indigo-200"
      >
        <Plus size={14} /> Allocate Funds
      </button>
    </div>
  );
}

export default function EnvelopeGrid() {
  const [envelopes, setEnvelopes] = useState<EnvelopeDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [allocateTarget, setAllocateTarget] = useState<EnvelopeDTO | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await api.envelopes.list();
      setEnvelopes(data);
    } catch { /* silent */ }
  }, []);

  useEffect(() => {
    load().finally(() => setLoading(false));
  }, [load]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="animate-spin text-indigo-400" size={28} />
      </div>
    );
  }

  return (
    <>
      <div className="rounded-xl border border-slate-700 bg-slate-900 p-5">
        <div className="mb-4 flex items-center gap-2">
          <Wallet size={20} className="text-indigo-400" />
          <h2 className="text-lg font-semibold text-slate-100">Envelopes</h2>
        </div>
        {!envelopes.length && (
          <p className="py-8 text-center text-sm text-slate-500">
            No envelopes yet. Create one to start budgeting.
          </p>
        )}
        <div className="grid gap-4 sm:grid-cols-2">
          {envelopes.map((e) => (
            <EnvelopeCard key={e.id} env={e} onAllocate={setAllocateTarget} />
          ))}
        </div>
      </div>

      {allocateTarget && (
        <AllocateModal
          envelope={allocateTarget}
          onClose={() => setAllocateTarget(null)}
          onDone={() => {
            setAllocateTarget(null);
            load();
          }}
        />
      )}
    </>
  );
}
