import { getSupabase } from "./supabase";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

/** Fetch wrapper — injects Supabase JWT in Authorization header. */
export async function apiFetch<T = unknown>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);

  const supabase = getSupabase();
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  headers.set("Content-Type", "application/json");

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.text();
    throw new ApiError(body || res.statusText, res.status);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

/** Upload a file (for PWA share_target). Sends multipart/form-data. */
export async function uploadReceipt(file: File): Promise<unknown> {
  const supabase = getSupabase();
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  const headers = new Headers();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const fd = new FormData();
  fd.append("file", file);

  const res = await fetch(`${API_BASE}/api/v1/transactions/upload-receipt`, {
    method: "POST",
    headers,
    body: fd,
  });

  if (!res.ok) {
    const body = await res.text();
    throw new ApiError(body || res.statusText, res.status);
  }
  return res.json();
}

// ── DTOs ───────────────────────────────────────────────────────────────────

export interface TransactionDTO {
  id: string;
  user_id: string;
  account_id: string | null;
  event_group_id: string | null;
  category_id: string | null;
  amount: number;
  currency: string;
  description: string;
  transaction_date: string;
  status: string;
  raw_data: Record<string, unknown> | null;
  created_at: string;
}

export interface CategoryDTO {
  id: string;
  user_id: string;
  name: string;
  color: string;
  icon: string;
  created_at: string;
}

export interface EnvelopeDTO {
  id: string;
  user_id: string;
  name: string;
  target_amount: string | null;
  current_balance: string;
  created_at: string;
  updated_at: string;
}

export interface RuleDTO {
  id: string;
  user_id: string;
  category_id: string;
  keyword: string;
  created_at: string;
}

// ── Typed endpoint helpers ─────────────────────────────────────────────────

export const api = {
  transactions: {
    list: () => apiFetch<TransactionDTO[]>("/api/v1/transactions"),
    create: (data: { amount: number; description?: string; transaction_date?: string }) =>
      apiFetch<TransactionDTO>("/api/v1/transactions", { method: "POST", body: JSON.stringify(data) }),
    netBalance: () =>
      apiFetch<{ net_balance: string; transaction_count: number }>("/api/v1/transactions/netting"),
  },
  categories: {
    list: () => apiFetch<CategoryDTO[]>("/api/v1/categories"),
    create: (data: { name: string; color?: string; icon?: string }) =>
      apiFetch<CategoryDTO>("/api/v1/categories", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: { name?: string; color?: string; icon?: string }) =>
      apiFetch<CategoryDTO>(`/api/v1/categories/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    delete: (id: string) =>
      apiFetch<void>(`/api/v1/categories/${id}`, { method: "DELETE" }),
  },
  rules: {
    list: () => apiFetch<RuleDTO[]>("/api/v1/rules"),
    create: (data: { category_id: string; keyword: string }) =>
      apiFetch<RuleDTO>("/api/v1/rules", { method: "POST", body: JSON.stringify(data) }),
    delete: (id: string) =>
      apiFetch<void>(`/api/v1/rules/${id}`, { method: "DELETE" }),
  },
  envelopes: {
    list: () => apiFetch<EnvelopeDTO[]>("/api/v1/envelopes"),
    allocate: (id: string, amount: number) =>
      apiFetch<EnvelopeDTO>(`/api/v1/envelopes/${id}/allocate`, {
        method: "POST",
        body: JSON.stringify({ amount }),
      }),
  },
};
