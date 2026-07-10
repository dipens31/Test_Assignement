"use client";

import { useEffect, useState } from "react";
import { booksApi } from "@/lib/api/books";
import type { Book, BookCreatePayload } from "@/lib/types";
import BookTable from "@/components/books/BookTable";
import BookForm from "@/components/books/BookForm";
import Modal from "@/components/ui/Modal";
import Alert from "@/components/ui/Alert";
import { SkeletonTable } from "@/components/ui/Skeleton";
import { useToast } from "@/components/ui/Toast";
import { Plus, Search, X, BookOpen, Pencil } from "lucide-react";
import DataTable, { Column, Action } from "@/components/ui/DataTable";

export default function BooksPage() {
  const { toast } = useToast();
  const [books, setBooks] = useState<Book[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const [editBook, setEditBook] = useState<Book | null>(null);
  const [search, setSearch] = useState("");
  const [authorSearch, setAuthorSearch] = useState("");
  const [availableOnly, setAvailableOnly] = useState(false);
  const [page, setPage] = useState(0);
  const limit = 5;

  const fetchBooks = async () => {
    setLoading(true); setError("");
    try {
      const data = await booksApi.list({ skip: page * limit, limit, title: search || undefined, author: authorSearch || undefined, available_only: availableOnly });
      setBooks(data.items); setTotal(data.total);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to load books.";
      setError(msg);
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchBooks(); }, [search, authorSearch, availableOnly, page]);

  const handleCreate = async (data: BookCreatePayload) => {
    await booksApi.create(data);
    setShowAdd(false);
    toast("success", "Book added to catalog.");
    fetchBooks();
  };

  const handleUpdate = async (data: BookCreatePayload) => {
    if (!editBook) return;
    await booksApi.update(editBook.id, data);
    setEditBook(null);
    toast("success", "Book updated successfully.");
    fetchBooks();
  };

  const hasFilters = search || authorSearch || availableOnly;
  const totalPages = Math.ceil(total / limit);
  const canPrev = page > 0;
  const canNext = page < totalPages - 1;

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="page-title">Books</h1>
          <p className="page-subtitle">{loading ? "Loading…" : `${total} title${total !== 1 ? "s" : ""} in catalog`}</p>
        </div>
        <button className="btn-primary" onClick={() => setShowAdd(true)}>
          <Plus className="w-4 h-4" /> Add Book
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 items-center">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
          <input className="input pl-9 w-56" placeholder="Search by title…" value={search} onChange={(e) => setSearch(e.target.value)} />
          {search && <button onClick={() => setSearch("")} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"><X className="w-3.5 h-3.5" /></button>}
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
          <input className="input pl-9 w-52" placeholder="Search by author…" value={authorSearch} onChange={(e) => setAuthorSearch(e.target.value)} />
          {authorSearch && <button onClick={() => setAuthorSearch("")} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"><X className="w-3.5 h-3.5" /></button>}
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-600 cursor-pointer select-none">
          <input type="checkbox" checked={availableOnly} onChange={(e) => setAvailableOnly(e.target.checked)} className="h-4 w-4 rounded accent-brand-600" />
          Available only
        </label>
        {hasFilters && (
          <button onClick={() => { setSearch(""); setAuthorSearch(""); setAvailableOnly(false); }} className="btn-ghost btn-sm text-slate-500">
            <X className="w-3.5 h-3.5" /> Clear
          </button>
        )}
      </div>

      {error && <Alert variant="error" message={error} onClose={() => setError("")} />}
      {loading ? <SkeletonTable rows={6} cols={7} /> : (
        <DataTable
          data={books}
          columns={[
            { key: "title", header: "Title", render: (book) => <span className="font-semibold text-slate-900 line-clamp-1" title={book.title}>{book.title}</span> },
            { key: "author", header: "Author", className: "text-slate-600" },
            { key: "isbn", header: "ISBN", render: (book) => <span className="text-slate-400 font-mono text-xs">{book.isbn ?? "—"}</span> },
            { key: "published_year", header: "Year", render: (book) => <span className="text-slate-400">{book.published_year ?? "—"}</span> },
            { key: "copies_total", header: "Total", className: "text-center text-slate-700" },
            { key: "copies_available", header: "Available", render: (book) => (
              <span className={book.copies_available > 0 ? "badge badge-green" : "badge badge-red"}>
                {book.copies_available} / {book.copies_total}
              </span>
            )},
          ]}
          actions={[
            { label: "Edit", icon: <Pencil className="w-3.5 h-3.5" />, onClick: setEditBook, className: "btn-ghost btn-sm inline-flex items-center gap-1" }
          ]}
          emptyMessage="No books found"
          emptyIcon={<BookOpen className="w-10 h-10 text-slate-300" />}
          emptyDescription="Add a book to get started."
        />
      )}

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

      {showAdd && (
        <Modal title="Add New Book" onClose={() => setShowAdd(false)}>
          <BookForm onSubmit={handleCreate} onCancel={() => setShowAdd(false)} submitLabel="Add Book" />
        </Modal>
      )}
      {editBook && (
        <Modal title="Edit Book" onClose={() => setEditBook(null)}>
          <BookForm initial={editBook} onSubmit={handleUpdate} onCancel={() => setEditBook(null)} submitLabel="Save Changes" />
        </Modal>
      )}
    </div>
  );
}
