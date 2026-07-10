import { api } from "./client";
import type {
  Book,
  BookCreatePayload,
  BookUpdatePayload,
  PaginatedResponse,
} from "../types";

const BASE = "/api/v1/books";

export interface ListBooksParams {
  skip?: number;
  limit?: number;
  title?: string;
  author?: string;
  available_only?: boolean;
}

export const booksApi = {
  list(params: ListBooksParams = {}): Promise<PaginatedResponse<Book>> {
    const q = new URLSearchParams();
    if (params.skip != null) q.set("skip", String(params.skip));
    if (params.limit != null) q.set("limit", String(params.limit));
    if (params.title) q.set("title", params.title);
    if (params.author) q.set("author", params.author);
    if (params.available_only) q.set("available_only", "true");
    const qs = q.toString();
    return api.get<PaginatedResponse<Book>>(`${BASE}${qs ? `?${qs}` : ""}`);
  },

  get(id: string): Promise<Book> {
    return api.get<Book>(`${BASE}/${id}`);
  },

  create(payload: BookCreatePayload): Promise<Book> {
    return api.post<Book>(BASE, payload);
  },

  update(id: string, payload: BookUpdatePayload): Promise<Book> {
    return api.put<Book>(`${BASE}/${id}`, payload);
  },
};
