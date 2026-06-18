"use client";

import { useCallback, useEffect, useState } from "react";
import { api, type CategoryDTO, type RuleDTO } from "@/lib/api";
import {
  Loader2,
  Plus,
  Trash2,
  Palette,
  Hash,
  Settings2,
} from "lucide-react";

// ── Color presets ───────────────────────────────────────────────────────────
const COLORS = [
  "#6366f1", "#8b5cf6", "#d946ef", "#ec4899",
  "#f43f5e", "#ef4444", "#f97316", "#eab308",
  "#22c55e", "#14b8a6", "#06b6d4", "#3b82f6",
];

// ── Category row ────────────────────────────────────────────────────────────

function CategoryRow({
  cat,
  onDelete,
}: {
  cat: CategoryDTO;
  onDelete: (id: string) => void;
}) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-3">
      <span
        className="h-5 w-5 rounded-full"
        style={{ backgroundColor: cat.color }}
      />
      <span className="flex-1 text-sm font-medium text-slate-200">
        {cat.name}
      </span>
      <span className="text-xs text-slate-500">{cat.icon}</span>
      <button
        onClick={() => onDelete(cat.id)}
        className="rounded p-1 text-slate-500 transition hover:bg-red-900/30 hover:text-red-400"
      >
        <Trash2 size={14} />
      </button>
    </div>
  );
}

// ── New Category form ──────────────────────────────────────────────────────

function NewCategoryForm({
  onCreated,
}: {
  onCreated: () => void;
}) {
  const [name, setName] = useState("");
  const [color, setColor] = useState(COLORS[0]);
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    try {
      await api.categories.create({ name: name.trim(), color });
      setName("");
      onCreated();
    } catch { /* silent */ }
    setSaving(false);
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-lg border border-slate-700 bg-slate-800/30 p-4">
      <h3 className="mb-3 text-sm font-semibold text-slate-300">New Category</h3>
      <div className="space-y-3">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Category name"
          className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-indigo-500"
        />
        <div className="flex flex-wrap gap-1.5">
          {COLORS.map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setColor(c)}
              className={`h-6 w-6 rounded-full border-2 transition ${
                color === c ? "border-white" : "border-transparent"
              }`}
              style={{ backgroundColor: c }}
            />
          ))}
        </div>
        <button
          type="submit"
          disabled={saving || !name.trim()}
          className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-indigo-500 disabled:opacity-50"
        >
          {saving ? <Loader2 size={12} className="animate-spin" /> : <Plus size={12} />}
          Add Category
        </button>
      </div>
    </form>
  );
}

// ── Rule row ────────────────────────────────────────────────────────────────

function RuleRow({
  rule,
  categories,
  onDelete,
}: {
  rule: RuleDTO;
  categories: CategoryDTO[];
  onDelete: (id: string) => void;
}) {
  const cat = categories.find((c) => c.id === rule.category_id);
  return (
    <div className="flex items-center gap-3 rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-3">
      {cat && (
        <span
          className="h-3 w-3 rounded-full"
          style={{ backgroundColor: cat.color }}
        />
      )}
      <code className="flex-1 text-sm font-mono text-slate-200">
        &ldquo;{rule.keyword}&rdquo;
      </code>
      <span className="text-xs text-slate-400">
        → {cat?.name || "deleted"}
      </span>
      <button
        onClick={() => onDelete(rule.id)}
        className="rounded p-1 text-slate-500 transition hover:bg-red-900/30 hover:text-red-400"
      >
        <Trash2 size={14} />
      </button>
    </div>
  );
}

// ── New Rule form ───────────────────────────────────────────────────────────

function NewRuleForm({
  categories,
  onCreated,
}: {
  categories: CategoryDTO[];
  onCreated: () => void;
}) {
  const [keyword, setKeyword] = useState("");
  const [categoryId, setCategoryId] = useState(categories[0]?.id || "");
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyword.trim() || !categoryId) return;
    setSaving(true);
    try {
      await api.rules.create({ category_id: categoryId, keyword: keyword.trim() });
      setKeyword("");
      onCreated();
    } catch { /* silent */ }
    setSaving(false);
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-lg border border-slate-700 bg-slate-800/30 p-4">
      <h3 className="mb-3 text-sm font-semibold text-slate-300">New Rule</h3>
      <div className="space-y-3">
        <input
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="e.g. AWS, Vercel, Uber"
          className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-indigo-500"
        />
        <select
          value={categoryId}
          onChange={(e) => setCategoryId(e.target.value)}
          className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 outline-none focus:border-indigo-500"
        >
          {categories.length === 0 && (
            <option value="">No categories — create one first</option>
          )}
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <button
          type="submit"
          disabled={saving || !keyword.trim() || !categoryId}
          className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-indigo-500 disabled:opacity-50"
        >
          {saving ? <Loader2 size={12} className="animate-spin" /> : <Plus size={12} />}
          Add Rule
        </button>
      </div>
    </form>
  );
}

// ── Page ─────────────────────────────────────────────────────────────────────

export default function RulesPage() {
  const [categories, setCategories] = useState<CategoryDTO[]>([]);
  const [rules, setRules] = useState<RuleDTO[]>([]);
  const [loading, setLoading] = useState(true);

  const loadAll = useCallback(async () => {
    try {
      const [cats, rls] = await Promise.all([api.categories.list(), api.rules.list()]);
      setCategories(cats);
      setRules(rls);
    } catch { /* silent */ }
  }, []);

  useEffect(() => {
    setLoading(true);
    loadAll().finally(() => setLoading(false));
  }, [loadAll]);

  const handleDeleteCategory = async (id: string) => {
    try {
      await api.categories.delete(id);
      await loadAll();
    } catch { /* silent */ }
  };

  const handleDeleteRule = async (id: string) => {
    try {
      await api.rules.delete(id);
      await loadAll();
    } catch { /* silent */ }
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center gap-2">
          <Settings2 className="text-indigo-400" size={22} />
          <h1 className="text-2xl font-bold text-slate-100">Rules &amp; Categories</h1>
        </div>
        <p className="mt-1 text-sm text-slate-400">
          Define categories and keyword rules for deterministic transaction matching.
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <Loader2 className="animate-spin text-indigo-400" size={28} />
        </div>
      ) : (
        <div className="grid gap-8 lg:grid-cols-2">
          {/* Categories */}
          <div className="space-y-4">
            <h2 className="flex items-center gap-1.5 text-sm font-semibold uppercase tracking-wider text-slate-400">
              <Palette size={16} /> Categories
            </h2>
            <NewCategoryForm onCreated={loadAll} />
            <div className="space-y-2">
              {categories.length === 0 && (
                <p className="py-4 text-center text-sm text-slate-500">No categories yet.</p>
              )}
              {categories.map((c) => (
                <CategoryRow key={c.id} cat={c} onDelete={handleDeleteCategory} />
              ))}
            </div>
          </div>

          {/* Rules */}
          <div className="space-y-4">
            <h2 className="flex items-center gap-1.5 text-sm font-semibold uppercase tracking-wider text-slate-400">
              <Hash size={16} /> Keyword Rules
            </h2>
            <NewRuleForm categories={categories} onCreated={loadAll} />
            <div className="space-y-2">
              {rules.length === 0 && (
                <p className="py-4 text-center text-sm text-slate-500">No rules yet. Add keywords to auto-categorize transactions.</p>
              )}
              {rules.map((r) => (
                <RuleRow
                  key={r.id}
                  rule={r}
                  categories={categories}
                  onDelete={handleDeleteRule}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
