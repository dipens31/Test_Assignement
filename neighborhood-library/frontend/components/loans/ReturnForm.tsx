"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import type { Loan, ReturnPayload } from "@/lib/types";
import Alert from "@/components/ui/Alert";
import Spinner from "@/components/ui/Spinner";
import { CheckCircle, DollarSign, Info } from "lucide-react";

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

interface ReturnFormProps {
  onSubmit: (data: ReturnPayload) => Promise<Loan>;
}

interface FormValues { loan_id: string; }

export default function ReturnForm({ onSubmit }: ReturnFormProps) {
  const [error, setError] = useState("");
  const [returnedLoan, setReturnedLoan] = useState<Loan | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormValues>();

  const submit = async (data: FormValues) => {
    setError(""); setReturnedLoan(null); setSubmitting(true);
    try {
      const loan = await onSubmit({ loan_id: data.loan_id.trim() });
      setReturnedLoan(loan);
      reset();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const fine = returnedLoan ? Number(returnedLoan.fine_amount) : 0;

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-5" noValidate>
      {error && <Alert variant="error" message={error} onClose={() => setError("")} />}

      {returnedLoan && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 space-y-3">
          <div className="flex items-center gap-2 text-emerald-700 font-semibold">
            <CheckCircle className="w-4 h-4" /> Book returned successfully!
          </div>
          <div className="text-sm text-emerald-800 space-y-1">
            <p>Book: <span className="font-medium">{returnedLoan.book?.title ?? returnedLoan.book_id}</span></p>
            <p>Member: <span className="font-medium">{returnedLoan.member?.name ?? returnedLoan.member_id}</span></p>
          </div>
          {fine > 0 ? (
            <div className="flex items-center gap-2 rounded-lg bg-red-50 border border-red-200 px-3 py-2">
              <DollarSign className="w-4 h-4 text-red-500" />
              <span className="text-sm font-semibold text-red-700">Overdue fine: ${fine.toFixed(2)}</span>
            </div>
          ) : (
            <p className="text-xs text-emerald-600">No overdue fine — returned on time.</p>
          )}
        </div>
      )}

      <div>
        <label className="label" htmlFor="loan_id">Loan ID <span className="text-red-500">*</span></label>
        <input
          id="loan_id"
          className={`input font-mono text-xs tracking-wide ${errors.loan_id ? "input-error" : ""}`}
          placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          autoComplete="off"
          {...register("loan_id", {
            required: "Loan ID is required",
            validate: (v) => UUID_RE.test(v.trim()) || "Must be a valid UUID (find it on the Loans page)",
          })}
        />
        {errors.loan_id
          ? <p className="field-error">{errors.loan_id.message}</p>
          : <p className="mt-1.5 flex items-center gap-1 text-xs text-slate-400"><Info className="w-3 h-3" /> Copy the Loan ID from the All Loans page.</p>}
      </div>

      <button type="submit" className="btn-primary w-full justify-center" disabled={submitting}>
        {submitting ? <><Spinner size="sm" className="mr-2" />Processing…</> : "Return Book"}
      </button>
    </form>
  );
}
