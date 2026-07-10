import { List, Copy, Check } from "lucide-react";
import type { Loan } from "@/lib/types";
import { useToast } from "@/components/ui/Toast";
import { useState } from "react";

interface LoanTableProps {
  loans: Loan[];
  showFine?: boolean;
}

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

export default function LoanTable({ loans, showFine = false }: LoanTableProps) {
  const { toast } = useToast();
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const copyId = async (id: string) => {
    await navigator.clipboard.writeText(id);
    setCopiedId(id);
    toast("success", "Loan ID copied to clipboard");
    setTimeout(() => setCopiedId(null), 2000);
  };
  if (loans.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-400 gap-3">
        <List className="w-10 h-10 text-slate-300" />
        <p className="font-medium">No loans found</p>
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Member</th>
            <th>Book</th>
            <th>Status</th>
            <th>Borrowed</th>
            <th>Due</th>
            <th>Returned</th>
            {showFine && <th className="text-right">Fine</th>}
          </tr>
        </thead>
        <tbody>
          {loans.map((loan) => (
            <tr key={loan.id}>
              <td>
                <button
                  onClick={() => copyId(loan.id)}
                  className="inline-flex items-center gap-1 text-xs font-mono text-slate-500 hover:text-brand-600 transition-colors group"
                  title="Copy Loan ID"
                >
                  <span className="truncate max-w-[100px]">{loan.id.slice(0, 8)}...</span>
                  {copiedId === loan.id ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100" />}
                </button>
              </td>
              <td><span className="font-semibold text-slate-900">{loan.member?.name ?? loan.member_id}</span></td>
              <td className="max-w-[200px]">
                <span className="truncate block" title={loan.book?.title}>{loan.book?.title ?? loan.book_id}</span>
              </td>
              <td>
                <span className={STATUS_BADGE[loan.status] ?? "badge badge-gray"}>
                  {STATUS_LABEL[loan.status] ?? loan.status}
                </span>
              </td>
              <td className="text-slate-500">{fmt(loan.borrowed_at)}</td>
              <td className={loan.status === "OVERDUE" ? "text-red-600 font-medium" : "text-slate-500"}>
                {fmt(loan.due_at)}
              </td>
              <td className="text-slate-500">{fmt(loan.returned_at)}</td>
              {showFine && (
                <td className="text-right">
                  {Number(loan.fine_amount) > 0 ? (
                    <span className="font-semibold text-red-600">${Number(loan.fine_amount).toFixed(2)}</span>
                  ) : (
                    <span className="text-slate-400">—</span>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
