import { NextRequest, NextResponse } from "next/server";
import { getSupabase } from "@/lib/supabase";

const BACKEND_URL = process.env.BACKEND_URL || "http://backend:8000";

/**
 * PWA share_target receiver.
 * Mobile OS shares file → this route captures it → POSTs to backend /api/v1/transactions/upload-receipt.
 */
export async function POST(req: NextRequest) {
  try {
    // 1. Extract file from multipart form
    const fd = await req.formData();
    const file = fd.get("file");
    if (!file || !(file instanceof File)) {
      return NextResponse.json({ error: "No file received" }, { status: 400 });
    }

    // 2. Get session JWT from Supabase
    const authHeader = req.headers.get("authorization") || "";
    let token = authHeader.replace("Bearer ", "");
    if (!token) {
      // Try reading from Supabase session cookie (if logged in via SSR)
      const supabase = getSupabase();
      const { data } = await supabase.auth.getSession();
      token = data.session?.access_token || "";
    }

    if (!token) {
      return NextResponse.redirect(new URL("/login", req.url));
    }

    // 3. Forward file to backend
    const forwardFd = new FormData();
    forwardFd.append("file", file, file.name);

    const backendRes = await fetch(`${BACKEND_URL}/api/v1/transactions/upload-receipt`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: forwardFd,
    });

    if (!backendRes.ok) {
      const errText = await backendRes.text();
      console.error("Backend upload failed:", errText);
      return NextResponse.json({ error: "Backend processing failed" }, { status: 502 });
    }

    const data = await backendRes.json();
    return NextResponse.redirect(new URL("/?receipt=ok", req.url));
  } catch (err) {
    console.error("Receipt route error:", err);
    return NextResponse.json({ error: "Internal error" }, { status: 500 });
  }
}
