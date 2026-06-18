"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Settings2,
  Link2,
  LogOut,
  Receipt,
  PiggyBank,
} from "lucide-react";

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/rules", label: "Rules & Categories", icon: Settings2 },
  { href: "/accounts", label: "Connections", icon: Link2 },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-60 flex-col border-r border-slate-800 bg-slate-900">
      {/* Brand */}
      <div className="flex items-center gap-2 border-b border-slate-800 px-5 py-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
          <Receipt size={16} className="text-white" />
        </div>
        <span className="text-lg font-bold text-slate-100">FinanceMacro</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                active
                  ? "bg-indigo-600/20 text-indigo-300"
                  : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              }`}
            >
              <Icon size={18} />
              {label}
            </Link>
          );
        })}

        {/* Spacer */}
        <div className="pt-6">
          <Link
            href="/login"
            className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-500 transition hover:bg-slate-800 hover:text-slate-300"
          >
            <LogOut size={18} />
            Sign Out
          </Link>
        </div>
      </nav>

      {/* Footer */}
      <div className="border-t border-slate-800 px-5 py-3">
        <p className="text-xs text-slate-600">v0.1.0</p>
      </div>
    </aside>
  );
}
