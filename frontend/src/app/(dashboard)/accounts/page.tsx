"use client";

import { useCallback, useEffect, useState } from "react";
import { api, type AccountDTO } from "@/lib/api";
import { Loader2, Plus, Trash2, Link2, Globe, Landmark } from "lucide-react";

const PROVIDER_META: Record<string, { label: string; icon: typeof Globe }> = {
  mercadopago: { label: "Mercado Pago", icon: Globe },
  invertironline: { label: "InvertirOnline", icon: Globe },
  bank: { label: "Bank", icon: Landmark },
  manual: { label: "Manual", icon: Link2 },
};

const PROVIDERS = ["mercadopago", "invertironline", "bank", "manual"];
const TYPES = ["checking", "savings", "investment", "credit"];

function AccountCard({ acct, onDelete }: { acct: AccountDTO; onDelete: (id: string) => void }) {
  const meta = PROVIDER_META[acct.provider] || { label: acct.provider, icon: Link2 };
  const Icon = meta.icon;

  return (
    <div className="flex items-center gap-4 rounded-xl border border-slate-700 bg-slate-800/50 p-4">
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-700">
        <Icon size={20} className="text-indigo-400" />
      </div>
      <div className="flex-1">
        <h3 className="font-medium text-slate-100">{meta.label}</h3>
        <p className="text-xs text-slate-500">
          {acct.type} {acct.name ? `— ${acct.name}` : ""}
        </p>
      </div>
      <button
        onClick={() => onDelete(acct.id)}
        className="rounded p-1.5 text-slate-500 transition hover:bg-red-900/30 hover:text-red-400"
      >
        <Trash2 size={15} />
      </button>
    </div>
  );
}

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<AccountDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [provider, setProvider] = useState("manual");
  const [type, setType] = useState("checking");
  const [name, setName] = useState("");

  const load = useCallback(async () => {
    try { setAccounts(await api.accounts.list()); } catch { /* silent */ }
  }, []);

  useEffect(() => { load().finally(() => setLoading(false)); }, [load]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.accounts.create({ provider, type, name: name.trim() || undefined });
      setShowForm(false);
      setName("");
      await load();
    } catch { /* silent */ }
  };

  const handleDelete = async (id: string) => {
    try { await api.accounts.delete(id); await load(); } catch { /* silent */ }
  };

  const webhookUrl = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/transactions/webhook/{provider}`;

  return (
    <div className="mx-auto max-w-4xl px-6 py-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Connections</h1>
          <p className="mt-1 text-sm text-slate-400">Link financial accounts and configure API integrations.</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-2 text-xs font-medium text-white hover:bg-indigo-500"
        >
          <Plus size={14} /> Add Account
        </button>
      </div>

      {/* Add form */}
      {showForm && (
        <form onSubmit={handleCreate} className="mb-6 rounded-xl border border-slate-700 bg-slate-900 p-5">
          <h3 className="mb-4 text-sm font-semibold text-slate-300">New Account</h3>
          <div className="grid gap-4 sm:grid-cols-3">
            <select value={provider} onChange={(e) => setProvider(e.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-500">
              {PROVIDERS.map((p) => <option key={p} value={p}>{PROVIDER_META[p]?.label || p}</option>)}
            </select>
            <select value={type} onChange={(e) => setType(e.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-500">
              {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
            <input value={name} onChange={(e) => setName(e.target.value)}
              placeholder="Account name (optional)"
              className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-indigo-500" />
          </div>
          <button type="submit"
            className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-medium text-white hover:bg-indigo-500">
            Save
          </button>
        </form>
      )}

      {/* Webhook info */}
      <div className="mb-6 rounded-xl border border-amber-900/40 bg-amber-900/10 p-4">
        <p className="text-xs font-medium text-amber-300">Webhook Endpoint</p>
        <code className="mt-1 block break-all rounded bg-slate-800 px-3 py-2 text-xs text-slate-300">
          {webhookUrl}
        </code>
        <p className="mt-2 text-xs text-slate-500">
          Replace <code className="text-slate-400">{`{provider}`}</code> with your provider slug. Configure this URL in your provider dashboard for automatic transaction ingesion.
        </p>
      </div>

      {/* Accounts list */}
      {loading ? (
        <div className="flex justify-center py-16"><Loader2 className="animate-spin text-indigo-400" size={28} /></div>
      ) : (
        <div className="space-y-3">
          {!accounts.length && (
            <p className="py-8 text-center text-sm text-slate-500">No accounts linked. Add one above.</p>
          )}
          {accounts.map((a) => <AccountCard key={a.id} acct={a} onDelete={handleDelete} />)}
        </div>
      )}
    </div>
  );
}
