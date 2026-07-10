"use client";

import { useEffect, useState } from "react";
import { loansApi } from "@/lib/api/loans";
import type { Loan, LoanStatus } from "@/lib/types";
import LoanTable from "@/components/loans/LoanTable";
import Alert from "@/components/ui/Alert";
import { SkeletonTable } from "@/components/ui/Skeleton";
import clsx from "clsx";

const STATUSES: { label: string; value: LoanStatus | ""; dot?: string }[] = [
  { label: "All Loans",  value: "" },
  { label: "Borrowed",   value: "BORROWED",  dot: "bg-brand-500" },
  { label: "Returned",   value: "RETURNED",  dot: "bg-slate-400" },
  { label: "Overdue",    value: "OVERDUE",   dot: "bg-red-500"   },
];

export default function LoansPage() {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [status, setStatus] = useState<LoanStatus | "">("");
  const [page, setPage] = useState(0);
  const limit = 5;

  const fetchLoans = async () => {
    setLoading(true); setError("");
    try {
      const data = await loansApi.list({ skip: page * limit, limit, status: status || undefined });
      setLoans(data.items); setTotal(data.total);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load loans.");
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchLoans(); }, [status, page]);

  const totalPages = Math.ceil(total / limit);
  const canPrev = page > 0;
  const canNext = page < totalPages - 1;

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  return (
    <div className="space-y-5">
      <div>
        <h1 className="page-title">All Loans</h1>
        <p className="page-subtitle">{loading ? "Loading…" : `${total} loan${total !== 1 ? "s" : ""}`}</p>
      </div>

      {/* Status tab pills */}
      <div className="flex gap-1.5 flex-wrap">
        {STATUSES.map(({ label, value, dot }) => (
          <button
            key={value}
            onClick={() => setStatus(value)}
            className={clsx(
              "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all",
              status === value
                ? "bg-brand-600 text-white shadow-sm"
                : "bg-white border border-slate-200 text-slate-600 hover:border-brand-300 hover:text-brand-700",
            )}
          >
            {dot && <span className={clsx("w-2 h-2 rounded-full", dot)} />}
            {label}
          </button>
        ))}
      </div>

      {error && <Alert variant="error" message={error} onClose={() => setError("")} />}
      {loading ? <SkeletonTable rows={6} cols={7} /> : <LoanTable loans={loans} showFine />}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-slate-500">
            Showing {page * limit + 1}-{Math.min((page + 1) * limit, total)} of {total}
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={!canPrev}
              className="btn-ghost btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="text-sm text-slate-600">
              Page {page + 1} of {totalPages}
            </span>
            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={!canNext}
              className="btn-ghost btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
