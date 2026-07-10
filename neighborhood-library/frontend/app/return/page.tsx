"use client";

import { loansApi } from "@/lib/api/loans";
import type { Loan, ReturnPayload } from "@/lib/types";
import ReturnForm from "@/components/loans/ReturnForm";
import Link from "next/link";
import { CornerDownLeft, ArrowRight } from "lucide-react";

export default function ReturnPage() {
  const handleReturn = async (data: ReturnPayload): Promise<Loan> => {
    return loansApi.returnBook(data);
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6 flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50">
          <CornerDownLeft className="w-5 h-5 text-amber-600" />
        </span>
        <div>
          <h1 className="page-title">Return a Book</h1>
          <p className="page-subtitle">Process a book return and calculate any overdue fines.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        {/* Form */}
        <div className="md:col-span-3 card card-body">
          <ReturnForm onSubmit={handleReturn} />
        </div>

        {/* Sidebar */}
        <aside className="md:col-span-2 space-y-4">
          <div className="card card-body text-sm space-y-3">
            <p className="font-semibold text-slate-800 text-xs uppercase tracking-wide">How to return</p>
            <ol className="list-decimal list-inside space-y-2 text-slate-600">
              <li>Go to <Link href="/loans" className="text-brand-600 hover:underline inline-flex items-center gap-0.5">All Loans <ArrowRight className="w-3 h-3" /></Link> and find the active loan.</li>
              <li>Copy the Loan ID from the table.</li>
              <li>Paste it into the form and click <strong>Return Book</strong>.</li>
            </ol>
          </div>
          <div className="card card-body text-sm space-y-1">
            <p className="font-semibold text-slate-800 text-xs uppercase tracking-wide mb-2">Fine policy</p>
            <p className="text-slate-500">Overdue fines accrue at <strong>$0.50 per day</strong> past the due date and are shown immediately after processing the return.</p>
          </div>
        </aside>
      </div>
    </div>
  );
}
