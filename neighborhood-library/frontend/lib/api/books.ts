import { api } from "./client";
import { API_ENDPOINTS } from "../constants";
import type {
  Book,
  BookCreatePayload,
  BookUpdatePayload,
  PaginatedResponse,
} from "../types";

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
    return api.get<PaginatedResponse<Book>>(`${API_ENDPOINTS.BOOKS}${qs ? `?${qs}` : ""}`);
  },

  get(id: string): Promise<Book> {
    return api.get<Book>(API_ENDPOINTS.BOOKS_DETAIL(id));
  },

  create(payload: BookCreatePayload): Promise<Book> {
    return api.post<Book>(API_ENDPOINTS.BOOKS, payload);
  },

  update(id: string, payload: BookUpdatePayload): Promise<Book> {
    return api.put<Book>(API_ENDPOINTS.BOOKS_DETAIL(id), payload);
  },
};
