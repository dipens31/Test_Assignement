// ── Shared domain types matching backend Pydantic schemas ─────────────────────

export type LoanStatus = "BORROWED" | "RETURNED" | "OVERDUE";

export interface Book {
  id: string;
  title: string;
  author: string;
  isbn: string | null;
  published_year: number | null;
  copies_total: number;
  copies_available: number;
  created_at: string;
  updated_at: string;
}

export interface Member {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  address: string | null;
  created_at: string;
  updated_at: string;
}

export interface Loan {
  id: string;
  member_id: string;
  book_id: string;
  borrowed_at: string;
  due_at: string | null;
  returned_at: string | null;
  status: LoanStatus;
  fine_amount: string;
  member: Member;
  book: Book;
}

export interface PaginatedResponse<T> {
  total: number;
  skip: number;
  limit: number;
  items: T[];
}

// ── Request payload types ─────────────────────────────────────────────────────

export interface BookCreatePayload {
  title: string;
  author: string;
  isbn?: string;
  published_year?: number;
  copies_total: number;
}

export interface BookUpdatePayload {
  title?: string;
  author?: string;
  isbn?: string;
  published_year?: number;
  copies_total?: number;
}

export interface MemberCreatePayload {
  name: string;
  email: string;
  phone?: string;
  address?: string;
}

export interface MemberUpdatePayload {
  name?: string;
  email?: string;
  phone?: string;
  address?: string;
}

export interface BorrowPayload {
  member_id: string;
  book_id: string;
  due_at?: string;
}

export interface ReturnPayload {
  loan_id: string;
}

// ── Generic API error ─────────────────────────────────────────────────────────

export interface ApiError {
  detail: string;
}
