"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { BookOpen, Users, BookMarked, CornerDownLeft, List, AlertOctagon, Library } from "lucide-react";

const navLinks = [
  { href: "/books",         label: "Books",         icon: BookOpen      },
  { href: "/members",       label: "Members",       icon: Users         },
  { href: "/borrow",        label: "Borrow",        icon: BookMarked    },
  { href: "/return",        label: "Return",        icon: CornerDownLeft },
  { href: "/loans",         label: "All Loans",     icon: List          },
  { href: "/loans/overdue", label: "Overdue",       icon: AlertOctagon  },
];

export default function Navbar() {
  const pathname = usePathname();

  const isActive = (href: string) =>
    href === "/loans" ? pathname === "/loans" : pathname === href || pathname.startsWith(href + "/");

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-14">
        <Link href="/" className="flex items-center gap-2 group">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white shadow-sm group-hover:bg-brand-700 transition-colors">
            <Library className="w-4 h-4" />
          </span>
          <span className="font-bold text-slate-900 tracking-tight">LibraryHub</span>
        </Link>

        <nav className="hidden md:flex items-center gap-0.5">
          {navLinks.map(({ href, label, icon: Icon }) => {
            const active = isActive(href);
            return (
              <Link
                key={href}
                href={href}
                className={clsx(
                  "flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150",
                  active
                    ? "bg-brand-50 text-brand-700"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
                )}
              >
                <Icon className={clsx("w-4 h-4", active ? "text-brand-600" : "text-slate-400")} />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* Mobile: icon strip */}
        <nav className="flex md:hidden items-center gap-0.5">
          {navLinks.map(({ href, icon: Icon, label }) => {
            const active = isActive(href);
            return (
              <Link
                key={href}
                href={href}
                title={label}
                className={clsx(
                  "p-2 rounded-lg transition-colors",
                  active ? "bg-brand-50 text-brand-700" : "text-slate-500 hover:bg-slate-100",
                )}
              >
                <Icon className="w-4 h-4" />
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
