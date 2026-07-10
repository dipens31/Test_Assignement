"use client";

import { useForm } from "react-hook-form";
import type { Book, BookCreatePayload } from "@/lib/types";
import Alert from "@/components/ui/Alert";
import Spinner from "@/components/ui/Spinner";
import { useState } from "react";

interface BookFormProps {
  initial?: Partial<Book>;
  onSubmit: (data: BookCreatePayload) => Promise<void>;
  onCancel?: () => void;
  submitLabel?: string;
}

export default function BookForm({
  initial,
  onSubmit,
  onCancel,
  submitLabel = "Save",
}: BookFormProps) {
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<BookCreatePayload>({
    defaultValues: {
      title: initial?.title ?? "",
      author: initial?.author ?? "",
      isbn: initial?.isbn ?? "",
      published_year: initial?.published_year ?? undefined,
      copies_total: initial?.copies_total ?? 1,
    },
  });

  const submit = async (data: BookCreatePayload) => {
    setError("");
    setSubmitting(true);
    try {
      const payload: BookCreatePayload = {
        title: data.title.trim(),
        author: data.author.trim(),
        isbn: data.isbn?.trim() || undefined,
        published_year: data.published_year ? Number(data.published_year) : undefined,
        copies_total: Number(data.copies_total),
      };
      await onSubmit(payload);
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
        <label className="label" htmlFor="title">Title <span className="text-red-500">*</span></label>
        <input
          id="title"
          className={`input ${errors.title ? "input-error" : ""}`}
          placeholder="e.g. The Pragmatic Programmer"
          {...register("title", { 
            required: "Title is required",
            validate: (value) => value.trim().length > 0 || "Title cannot be empty or whitespace only"
          })}
        />
        {errors.title && <p className="field-error">{errors.title.message}</p>}
      </div>

      <div>
        <label className="label" htmlFor="author">Author <span className="text-red-500">*</span></label>
        <input
          id="author"
          className={`input ${errors.author ? "input-error" : ""}`}
          placeholder="e.g. David Thomas, Andrew Hunt"
          {...register("author", { 
            required: "Author is required",
            validate: (value: string) => value.trim().length > 0 || "Author cannot be empty or whitespace only"
          })}
        />
        {errors.author && <p className="field-error">{errors.author.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label" htmlFor="isbn">ISBN <span className="text-slate-400 font-normal text-xs">(optional)</span></label>
          <input id="isbn" className="input" placeholder="e.g. 978-0-13-595705-9" {...register("isbn")} />
        </div>
        <div>
          <label className="label" htmlFor="published_year">Year <span className="text-slate-400 font-normal text-xs">(optional)</span></label>
          <input
            id="published_year"
            type="number"
            className={`input ${errors.published_year ? "input-error" : ""}`}
            placeholder="e.g. 2019"
            {...register("published_year", { min: { value: 1000, message: "Invalid year" }, max: { value: 9999, message: "Invalid year" } })}
          />
          {errors.published_year && <p className="field-error">{errors.published_year.message}</p>}
        </div>
      </div>

      <div>
        <label className="label" htmlFor="copies_total">Number of Copies <span className="text-red-500">*</span></label>
        <input
          id="copies_total"
          type="number"
          className={`input ${errors.copies_total ? "input-error" : ""}`}
          placeholder="e.g. 2"
          min={1}
          {...register("copies_total", {
            required: "Copies is required",
            min: { value: 1, message: "Must have at least 1 copy" },
          })}
        />
        {errors.copies_total && <p className="field-error">{errors.copies_total.message}</p>}
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
