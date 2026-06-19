"use client";

import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from "recharts";
import type { TransactionDTO } from "@/lib/api";

interface Props {
  transactions: TransactionDTO[];
}

interface DailyBucket {
  date: string;
  income: number;
  expense: number;
}

function groupByDay(txs: TransactionDTO[]): DailyBucket[] {
  const map = new Map<string, { income: number; expense: number }>();

  for (const tx of txs) {
    const day = tx.transaction_date.slice(0, 10); // YYYY-MM-DD
    const entry = map.get(day) ?? { income: 0, expense: 0 };
    if (tx.amount > 0) entry.income += tx.amount;
    else entry.expense += Math.abs(tx.amount);
    map.set(day, entry);
  }

  return Array.from(map.entries())
    .map(([date, v]) => ({ date, income: +v.income.toFixed(2), expense: +v.expense.toFixed(2) }))
    .sort((a, b) => a.date.localeCompare(b.date));
}

const fmt = (v: number) => `$${v.toFixed(0)}`;

export default function CashFlowChart({ transactions }: Props) {
  const data = groupByDay(transactions);

  if (!data.length) {
    return (
      <div className="rounded-xl border border-slate-700 bg-slate-900 p-5">
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-400">
          Cash Flow
        </h3>
        <p className="py-8 text-center text-sm text-slate-500">
          No transaction data for this period.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900 p-5">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">
        Daily Cash Flow
      </h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} barCategoryGap={4}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="date"
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            tickLine={false}
            axisLine={{ stroke: "#334155" }}
          />
          <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} tickFormatter={fmt} axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: "#e2e8f0" }}
            formatter={(value: unknown) => [`$${Number(value).toFixed(2)}`]}
          />
          <Legend
            wrapperStyle={{ fontSize: 11, color: "#94a3b8" }}
            iconType="rect"
            formatter={(v: string) => v.charAt(0).toUpperCase() + v.slice(1)}
          />
          <Bar dataKey="income" fill="#34d399" radius={[4, 4, 0, 0]} name="Income" />
          <Bar dataKey="expense" fill="#f87171" radius={[4, 4, 0, 0]} name="Expenses" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
