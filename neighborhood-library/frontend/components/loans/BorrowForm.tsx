"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import type { BorrowPayload } from "@/lib/types";
import Alert from "@/components/ui/Alert";
import Spinner from "@/components/ui/Spinner";
import { Info } from "lucide-react";

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

interface BorrowFormProps {
  onSubmit: (data: BorrowPayload) => Promise<void>;
  onSuccess?: () => void;
}

interface FormValues {
  member_id: string;
  book_id: string;
  due_at: string;
}

const minDue = () => {
  const d = new Date();
  d.setMinutes(d.getMinutes() + 1);
  return d.toISOString().slice(0, 16);
};

export default function BorrowForm({ onSubmit, onSuccess }: BorrowFormProps) {
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormValues>();

  const submit = async (data: FormValues) => {
    setError(""); setSuccess(""); setSubmitting(true);
    try {
      await onSubmit({ member_id: data.member_id.trim(), book_id: data.book_id.trim(), due_at: data.due_at || undefined });
      setSuccess("Book borrowed successfully! The loan has been recorded.");
      reset();
      onSuccess?.();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-5" noValidate>
      {error   && <Alert variant="error"   message={error}   onClose={() => setError("")} />}
      {success && <Alert variant="success" message={success} onClose={() => setSuccess("")} />}

      <div>
        <label className="label" htmlFor="member_id">Member ID <span className="text-red-500">*</span></label>
        <input
          id="member_id"
          className={`input font-mono text-xs tracking-wide ${errors.member_id ? "input-error" : ""}`}
          placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          autoComplete="off"
          {...register("member_id", {
            required: "Member ID is required",
            validate: (v) => UUID_RE.test(v.trim()) || "Must be a valid UUID (find it on the Members page)",
          })}
        />
        {errors.member_id
          ? <p className="field-error">{errors.member_id.message}</p>
          : <p className="mt-1.5 flex items-center gap-1 text-xs text-slate-400"><Info className="w-3 h-3" /> Copy the Member ID from the Members page.</p>}
      </div>

      <div>
        <label className="label" htmlFor="book_id">Book ID <span className="text-red-500">*</span></label>
        <input
          id="book_id"
          className={`input font-mono text-xs tracking-wide ${errors.book_id ? "input-error" : ""}`}
          placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          autoComplete="off"
          {...register("book_id", {
            required: "Book ID is required",
            validate: (v) => UUID_RE.test(v.trim()) || "Must be a valid UUID (find it on the Books page)",
          })}
        />
        {errors.book_id
          ? <p className="field-error">{errors.book_id.message}</p>
          : <p className="mt-1.5 flex items-center gap-1 text-xs text-slate-400"><Info className="w-3 h-3" /> Copy the Book ID from the Books page.</p>}
      </div>

      <div>
        <label className="label" htmlFor="due_at">Due Date <span className="text-slate-400 font-normal text-xs">(optional — defaults to 14 days)</span></label>
        <input id="due_at" type="datetime-local" className="input" min={minDue()} {...register("due_at")} />
      </div>

      <button type="submit" className="btn-primary w-full justify-center" disabled={submitting}>
        {submitting ? <><Spinner size="sm" className="mr-2" />Processing…</> : "Borrow Book"}
      </button>
    </form>
  );
}
