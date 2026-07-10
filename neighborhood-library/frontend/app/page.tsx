"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { booksApi } from "@/lib/api/books";
import { membersApi } from "@/lib/api/members";
import { loansApi } from "@/lib/api/loans";
import { BookOpen, Users, BookMarked, AlertOctagon, CornerDownLeft, List, ArrowRight } from "lucide-react";
import { SkeletonCards } from "@/components/ui/Skeleton";

interface Stats {
  books: number;
  members: number;
  activeLoans: number;
  overdue: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    Promise.all([
      booksApi.list({ limit: 1 }),
      membersApi.list({ limit: 1 }),
      loansApi.list({ limit: 1, status: "BORROWED" }),
      loansApi.overdue(),
    ]).then(([b, m, l, o]) =>
      setStats({ books: b.total, members: m.total, activeLoans: l.total, overdue: o.length }),
    ).catch(() => setStats({ books: 0, members: 0, activeLoans: 0, overdue: 0 }));
  }, []);

  const statCards = [
    { label: "Books in Catalog", value: stats?.books, icon: BookOpen,     bg: "bg-brand-50",   iconColor: "text-brand-600"   },
    { label: "Registered Members", value: stats?.members, icon: Users,    bg: "bg-violet-50",  iconColor: "text-violet-600"  },
    { label: "Active Loans",  value: stats?.activeLoans, icon: BookMarked, bg: "bg-emerald-50", iconColor: "text-emerald-600" },
    { label: "Overdue Items", value: stats?.overdue,     icon: AlertOctagon, bg: "bg-red-50",   iconColor: "text-red-600"   },
  ];

  const actions = [
    { href: "/books",         label: "Manage Books",    desc: "Browse catalog, add & edit titles",      icon: BookOpen,      accent: "border-l-brand-500"   },
    { href: "/members",       label: "Manage Members",  desc: "Register and update library members",    icon: Users,         accent: "border-l-violet-500"  },
    { href: "/borrow",        label: "Borrow a Book",   desc: "Check out a book for a member",          icon: BookMarked,    accent: "border-l-emerald-500" },
    { href: "/return",        label: "Return a Book",   desc: "Process return & calculate fines",       icon: CornerDownLeft, accent: "border-l-amber-500"  },
    { href: "/loans",         label: "All Loans",       desc: "Full borrowing history & filters",       icon: List,          accent: "border-l-slate-400"   },
    { href: "/loans/overdue", label: "Overdue Loans",   desc: "Overdue items & outstanding fines",      icon: AlertOctagon,  accent: "border-l-red-500"     },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Dashboard</h1>
        <p className="mt-1 text-sm text-slate-500">Welcome back — here&apos;s what&apos;s happening in your library.</p>
      </div>

      {/* Stats */}
      {stats === null ? (
        <SkeletonCards count={4} />
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {statCards.map(({ label, value, icon: Icon, bg, iconColor }) => (
            <div key={label} className="stat-card">
              <span className={`stat-icon ${bg}`}>
                <Icon className={`w-5 h-5 ${iconColor}`} />
              </span>
              <div>
                <p className="text-xs text-slate-500 font-medium">{label}</p>
                <p className="text-2xl font-bold text-slate-900 mt-0.5">{value ?? 0}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Quick actions */}
      <div>
        <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {actions.map(({ href, label, desc, icon: Icon, accent }) => (
            <Link
              key={href}
              href={href}
              className={`group card flex items-center gap-4 p-4 border-l-4 ${accent} hover:shadow-md transition-all duration-200`}
            >
              <Icon className="w-5 h-5 text-slate-400 group-hover:text-brand-600 transition-colors flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-slate-900 text-sm">{label}</p>
                <p className="text-xs text-slate-500 mt-0.5 truncate">{desc}</p>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-brand-500 transition-colors flex-shrink-0" />
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
