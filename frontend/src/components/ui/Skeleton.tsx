"use client";

/**
 * Generic skeleton components for loading states.
 * Mimics content shapes without layout shift.
 */

function SkeletonRow() {
  return (
    <tr className="border-b border-slate-800 last:border-0">
      <td className="px-5 py-3">
        <div className="h-4 w-20 animate-pulse rounded bg-slate-700" />
      </td>
      <td className="px-5 py-3">
        <div className="h-4 w-48 animate-pulse rounded bg-slate-700" />
      </td>
      <td className="px-5 py-3">
        <div className="h-5 w-16 animate-pulse rounded-full bg-slate-700" />
      </td>
      <td className="px-5 py-3 text-right">
        <div className="ml-auto h-4 w-16 animate-pulse rounded bg-slate-700" />
      </td>
      <td className="px-5 py-3 text-center">
        <div className="mx-auto h-5 w-20 animate-pulse rounded-full bg-slate-700" />
      </td>
    </tr>
  );
}

function SkeletonCard() {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-4">
      <div className="mb-3 flex items-center gap-2">
        <div className="h-4 w-4 animate-pulse rounded bg-slate-700" />
        <div className="h-4 w-24 animate-pulse rounded bg-slate-700" />
      </div>
      <div className="mb-2 h-8 w-32 animate-pulse rounded bg-slate-700" />
      <div className="mb-3 h-2 w-full animate-pulse rounded-full bg-slate-700" />
      <div className="h-8 w-full animate-pulse rounded-lg bg-slate-700" />
    </div>
  );
}

function SkeletonTickerRow() {
  return (
    <div className="flex items-center justify-between gap-4 rounded-lg bg-slate-800/60 px-4 py-3 text-sm">
      <div className="h-4 w-16 animate-pulse rounded bg-slate-700" />
      <div className="h-4 w-20 animate-pulse rounded bg-slate-700" />
      <div className="h-4 w-14 animate-pulse rounded bg-slate-700" />
    </div>
  );
}

function SkeletonStatCard() {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
      <div className="mb-2 flex items-center gap-2">
        <div className="h-4 w-4 animate-pulse rounded bg-slate-700" />
        <div className="h-3 w-20 animate-pulse rounded bg-slate-700" />
      </div>
      <div className="h-8 w-28 animate-pulse rounded bg-slate-700" />
    </div>
  );
}

export const Skeleton = {
  Row: SkeletonRow,
  Card: SkeletonCard,
  TickerRow: SkeletonTickerRow,
  StatCard: SkeletonStatCard,
};
