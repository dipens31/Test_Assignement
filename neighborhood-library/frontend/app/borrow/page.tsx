"use client";

import { loansApi } from "@/lib/api/loans";
import type { BorrowPayload } from "@/lib/types";
import BorrowForm from "@/components/loans/BorrowForm";
import Link from "next/link";
import { BookMarked, ArrowRight } from "lucide-react";

export default function BorrowPage() {
  const handleBorrow = async (data: BorrowPayload) => {
    await loansApi.borrow(data);
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6 flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50">
          <BookMarked className="w-5 h-5 text-emerald-600" />
        </span>
        <div>
          <h1 className="page-title">Borrow a Book</h1>
          <p className="page-subtitle">Check out a book for a library member.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        {/* Form */}
        <div className="md:col-span-3 card card-body">
          <BorrowForm onSubmit={handleBorrow} />
        </div>

        {/* Sidebar instructions */}
        <aside className="md:col-span-2 space-y-4">
          <div className="card card-body text-sm text-slate-600 space-y-3">
            <p className="font-semibold text-slate-800 text-xs uppercase tracking-wide">How to borrow</p>
            <ol className="list-decimal list-inside space-y-2 text-slate-600">
              <li>Go to the <Link href="/members" className="text-brand-600 hover:underline inline-flex items-center gap-0.5">Members page <ArrowRight className="w-3 h-3" /></Link> and copy the Member ID.</li>
              <li>Go to the <Link href="/books" className="text-brand-600 hover:underline inline-flex items-center gap-0.5">Books page <ArrowRight className="w-3 h-3" /></Link> and copy the Book ID.</li>
              <li>Paste both IDs into the form and set a due date (optional).</li>
              <li>Click <strong>Borrow Book</strong> to create the loan.</li>
            </ol>
          </div>
          <div className="card card-body text-sm">
            <p className="font-semibold text-slate-800 text-xs uppercase tracking-wide mb-2">Default due date</p>
            <p className="text-slate-500">If no due date is set, the loan defaults to <strong>14 days</strong> from today.</p>
          </div>
        </aside>
      </div>
    </div>
  );
}
