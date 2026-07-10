/**
 * Centralized API endpoint constants
 * All API paths should be defined here to avoid hardcoding
 */

export const API_ENDPOINTS = {
  BOOKS: "/api/v1/books",
  MEMBERS: "/api/v1/members",
  LOANS: "/api/v1/loans",
  MEMBERS_LOANS: (memberId: string) => `/api/v1/members/${memberId}/loans`,
  LOANS_BORROW: "/api/v1/loans/borrow",
  LOANS_RETURN: "/api/v1/loans/return",
  LOANS_OVERDUE: "/api/v1/loans/overdue",
  LOANS_DETAIL: (loanId: string) => `/api/v1/loans/${loanId}`,
  BOOKS_DETAIL: (bookId: string) => `/api/v1/books/${bookId}`,
  MEMBERS_DETAIL: (memberId: string) => `/api/v1/members/${memberId}`,
} as const;

export type ApiEndpoint = typeof API_ENDPOINTS;
