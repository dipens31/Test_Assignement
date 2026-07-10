import { BookOpen, Pencil, Copy, Check } from "lucide-react";
import type { Book } from "@/lib/types";
import { useToast } from "@/components/ui/Toast";
import { useState } from "react";

interface BookTableProps {
  books: Book[];
  onEdit?: (book: Book) => void;
}

export default function BookTable({ books, onEdit }: BookTableProps) {
  const { toast } = useToast();
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const copyId = async (id: string) => {
    await navigator.clipboard.writeText(id);
    setCopiedId(id);
    toast("success", "Book ID copied to clipboard");
    setTimeout(() => setCopiedId(null), 2000);
  };
  if (books.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-400 gap-3">
        <BookOpen className="w-10 h-10 text-slate-300" />
        <p className="font-medium">No books found</p>
        <p className="text-sm">Add a book to get started.</p>
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Author</th>
            <th>ISBN</th>
            <th>Year</th>
            <th className="text-center">Total</th>
            <th className="text-center">Available</th>
            {onEdit && <th />}
          </tr>
        </thead>
        <tbody>
          {books.map((book) => (
            <tr key={book.id}>
              <td>
                <button
                  onClick={() => copyId(book.id)}
                  className="inline-flex items-center gap-1 text-xs font-mono text-slate-500 hover:text-brand-600 transition-colors group"
                  title="Copy Book ID"
                >
                  <span className="truncate max-w-[100px]">{book.id.slice(0, 8)}...</span>
                  {copiedId === book.id ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100" />}
                </button>
              </td>
              <td>
                <span className="font-semibold text-slate-900 line-clamp-1" title={book.title}>{book.title}</span>
              </td>
              <td className="text-slate-600">{book.author}</td>
              <td className="text-slate-400 font-mono text-xs">{book.isbn ?? "—"}</td>
              <td className="text-slate-400">{book.published_year ?? "—"}</td>
              <td className="text-center text-slate-700">{book.copies_total}</td>
              <td className="text-center">
                <span className={book.copies_available > 0 ? "badge badge-green" : "badge badge-red"}>
                  {book.copies_available} / {book.copies_total}
                </span>
              </td>
              {onEdit && (
                <td className="text-right pr-4">
                  <button
                    onClick={() => onEdit(book)}
                    className="btn-ghost btn-sm inline-flex items-center gap-1"
                    title="Edit book"
                  >
                    <Pencil className="w-3.5 h-3.5" /> Edit
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
