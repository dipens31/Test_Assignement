import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import { ToastProvider } from "@/components/ui/Toast";

export const metadata: Metadata = {
  title: "LibraryHub — Neighborhood Library",
  description: "Manage books, members, and lending operations",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-slate-50">
        <ToastProvider>
          <Navbar />
          <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
          <footer className="border-t border-slate-200 py-4 text-center text-xs text-slate-400">
            © {new Date().getFullYear()} LibraryHub · Neighborhood Library Service
          </footer>
        </ToastProvider>
      </body>
    </html>
  );
}
