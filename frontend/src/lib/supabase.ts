import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn("Supabase env vars not set. Auth disabled.");
}

export const supabase = supabaseUrl
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

export function getSupabase() {
  if (!supabase) throw new Error("Supabase not configured. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY.");
  return supabase;
}
