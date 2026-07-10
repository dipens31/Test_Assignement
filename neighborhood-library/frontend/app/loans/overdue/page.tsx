"use client";

import { useEffect, useState } from "react";
import { loansApi } from "@/lib/api/loans";
import type { Loan } from "@/lib/types";
import Alert from "@/components/ui/Alert";
import { SkeletonTable } from "@/components/ui/Skeleton";
import { AlertOctagon, CheckCircle, RefreshCw, DollarSign, List } from "lucide-react";
import DataTable, { Column } from "@/components/ui/DataTable";

const STATUS_BADGE: Record<string, string> = {
  BORROWED: "badge badge-blue",
  RETURNED: "badge badge-gray",
  OVERDUE:  "badge badge-red",
};

const STATUS_LABEL: Record<string, string> = {
  BORROWED: "Borrowed",
  RETURNED: "Returned",
  OVERDUE:  "Overdue",
};

function fmt(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

export default function OverduePage() {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchOverdue = async () => {
    setLoading(true); setError("");
    try { setLoans(await loansApi.overdue()); }
    catch (e: unknown) { setError(e instanceof Error ? e.message : "Failed to load overdue loans."); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchOverdue(); }, []);

  const totalFine = loans.reduce((sum, l) => sum + Number(l.fine_amount), 0);

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-red-50">
            <AlertOctagon className="w-5 h-5 text-red-500" />
          </span>
          <div>
            <h1 className="page-title">Overdue Loans</h1>
            <p className="page-subtitle">
              {loading ? "Loading…" : `${loans.length} overdue loan${loans.length !== 1 ? "s" : ""}`}
            </p>
          </div>
        </div>
        <button className="btn-secondary" onClick={fetchOverdue} disabled={loading}>
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} /> Refresh
        </button>
      </div>

      {/* Fine summary banner */}
      {!loading && totalFine > 0 && (
        <div className="flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3">
          <DollarSign className="w-4 h-4 text-red-500 flex-shrink-0" />
          <p className="text-sm font-semibold text-red-700">
            Total outstanding fines: <span className="text-base">${totalFine.toFixed(2)}</span>
          </p>
        </div>
      )}

      {error && <Alert variant="error" message={error} onClose={() => setError("")} />}

      {loading ? (
        <SkeletonTable rows={4} cols={7} />
      ) : loans.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 gap-3 text-slate-400">
          <CheckCircle className="w-12 h-12 text-emerald-300" />
          <p className="font-semibold text-slate-600">All clear!</p>
          <p className="text-sm">No overdue loans — great job keeping up.</p>
        </div>
      ) : (
        <DataTable
          data={loans}
          columns={[
            { key: "member", header: "Member", render: (loan) => <span className="font-semibold text-slate-900">{loan.member?.name ?? "Unknown"}</span> },
            { key: "book", header: "Book", render: (loan) => <span className="max-w-[200px] truncate block" title={loan.book?.title}>{loan.book?.title ?? "Unknown"}</span> },
            { key: "status", header: "Status", render: (loan) => (
              <span className={STATUS_BADGE[loan.status] ?? "badge badge-gray"}>
                {STATUS_LABEL[loan.status] ?? loan.status}
              </span>
            )},
            { key: "borrowed_at", header: "Borrowed", render: (loan) => <span className="text-slate-500">{fmt(loan.borrowed_at)}</span> },
            { key: "due_at", header: "Due", render: (loan) => <span className="text-red-600 font-medium">{fmt(loan.due_at)}</span> },
            { key: "fine_amount", header: "Fine", render: (loan) => (
              Number(loan.fine_amount) > 0 ? (
                <span className="font-semibold text-red-600">${Number(loan.fine_amount).toFixed(2)}</span>
              ) : (
                <span className="text-slate-400">—</span>
              )
            )},
          ]}
          emptyMessage="No overdue loans found"
          emptyIcon={<List className="w-10 h-10 text-slate-300" />}
        />
      )}
    </div>
  );
}
