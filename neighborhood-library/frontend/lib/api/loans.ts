import { api } from "./client";
import type {
  BorrowPayload,
  Loan,
  LoanStatus,
  PaginatedResponse,
  ReturnPayload,
} from "../types";

const BASE = "/api/v1/loans";

export interface ListLoansParams {
  skip?: number;
  limit?: number;
  member_id?: string;
  book_id?: string;
  status?: LoanStatus;
}

export const loansApi = {
  list(params: ListLoansParams = {}): Promise<PaginatedResponse<Loan>> {
    const q = new URLSearchParams();
    if (params.skip != null) q.set("skip", String(params.skip));
    if (params.limit != null) q.set("limit", String(params.limit));
    if (params.member_id) q.set("member_id", params.member_id);
    if (params.book_id) q.set("book_id", params.book_id);
    if (params.status) q.set("status", params.status);
    const qs = q.toString();
    return api.get<PaginatedResponse<Loan>>(`${BASE}${qs ? `?${qs}` : ""}`);
  },

  get(id: string): Promise<Loan> {
    return api.get<Loan>(`${BASE}/${id}`);
  },

  overdue(): Promise<Loan[]> {
    return api.get<Loan[]>(`${BASE}/overdue`);
  },

  borrow(payload: BorrowPayload): Promise<Loan> {
    return api.post<Loan>(`${BASE}/borrow`, payload);
  },

  returnBook(payload: ReturnPayload): Promise<Loan> {
    return api.post<Loan>(`${BASE}/return`, payload);
  },
};
