"use client";

import { useForm } from "react-hook-form";
import type { Member, MemberCreatePayload } from "@/lib/types";
import Alert from "@/components/ui/Alert";
import Spinner from "@/components/ui/Spinner";
import { useState } from "react";

interface MemberFormProps {
  initial?: Partial<Member>;
  onSubmit: (data: MemberCreatePayload) => Promise<void>;
  onCancel?: () => void;
  submitLabel?: string;
}

export default function MemberForm({
  initial,
  onSubmit,
  onCancel,
  submitLabel = "Save",
}: MemberFormProps) {
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<MemberCreatePayload>({
    defaultValues: {
      name: initial?.name ?? "",
      email: initial?.email ?? "",
      phone: initial?.phone ?? "",
      address: initial?.address ?? "",
    },
  });

  const submit = async (data: MemberCreatePayload) => {
    setError("");
    setSubmitting(true);
    try {
      await onSubmit({
        name: data.name.trim(),
        email: data.email.trim(),
        phone: data.phone?.trim() || undefined,
        address: data.address?.trim() || undefined,
      });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "An unexpected error occurred.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-4" noValidate>
      {error && <Alert variant="error" message={error} onClose={() => setError("")} />}

      <div>
        <label className="label" htmlFor="name">Full Name <span className="text-red-500">*</span></label>
        <input
          id="name"
          className={`input ${errors.name ? "input-error" : ""}`}
          placeholder="e.g. Alice Johnson"
          {...register("name", { 
            required: "Name is required",
            validate: (value: string) => value.trim().length > 0 || "Name cannot be empty or whitespace only"
          })}
        />
        {errors.name && <p className="field-error">{errors.name.message}</p>}
      </div>

      <div>
        <label className="label" htmlFor="email">Email <span className="text-red-500">*</span></label>
        <input
          id="email"
          type="email"
          className={`input ${errors.email ? "input-error" : ""}`}
          placeholder="e.g. alice@example.com"
          {...register("email", {
            required: "Email is required",
            pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: "Enter a valid email address" },
            validate: (value: string) => value.trim().length > 0 || "Email cannot be empty or whitespace only"
          })}
        />
        {errors.email && <p className="field-error">{errors.email.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label" htmlFor="phone">Phone <span className="text-slate-400 font-normal text-xs">(optional)</span></label>
          <input id="phone" className="input" placeholder="e.g. +1-555-0100" {...register("phone")} />
        </div>
        <div>
          <label className="label" htmlFor="address">Address <span className="text-slate-400 font-normal text-xs">(optional)</span></label>
          <input id="address" className="input" placeholder="e.g. 123 Main St" {...register("address")} />
        </div>
      </div>

      <div className="flex justify-end gap-3 pt-2 border-t border-slate-100">
        {onCancel && (
          <button type="button" className="btn-secondary" onClick={onCancel} disabled={submitting}>
            Cancel
          </button>
        )}
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? <><Spinner size="sm" className="mr-1" />Saving…</> : submitLabel}
        </button>
      </div>
    </form>
  );
}
