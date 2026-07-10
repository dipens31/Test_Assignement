/**
 * Unit tests for the loans API wrapper.
 */

import { loansApi } from "@/lib/api/loans";

const mockFetch = jest.fn();
global.fetch = mockFetch;

function mockOk(body: unknown) {
  const text = JSON.stringify(body);
  mockFetch.mockResolvedValueOnce({
    ok: true,
    status: 200,
    json: async () => body,
    text: async () => text,
  });
}

afterEach(() => jest.clearAllMocks());

describe("loansApi.list", () => {
  it("calls correct endpoint without params", async () => {
    mockOk({ total: 0, skip: 0, limit: 20, items: [] });
    await loansApi.list();
    expect(mockFetch).toHaveBeenCalledWith("/api/v1/loans", expect.any(Object));
  });

  it("appends status filter to query string", async () => {
    mockOk({ total: 0, skip: 0, limit: 20, items: [] });
    await loansApi.list({ status: "OVERDUE" });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("status=OVERDUE");
  });

  it("appends member_id filter", async () => {
    mockOk({ total: 0, skip: 0, limit: 20, items: [] });
    await loansApi.list({ member_id: "test-uuid" });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("member_id=test-uuid");
  });
});

describe("loansApi.overdue", () => {
  it("calls /api/v1/loans/overdue", async () => {
    mockOk([]);
    await loansApi.overdue();
    expect(mockFetch).toHaveBeenCalledWith("/api/v1/loans/overdue", expect.any(Object));
  });
});

describe("loansApi.borrow", () => {
  it("sends POST to /borrow with payload", async () => {
    const loan = { id: "loan-id", status: "BORROWED" };
    mockOk(loan);
    const result = await loansApi.borrow({ member_id: "m1", book_id: "b1" });
    expect(result).toEqual(loan);
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe("/api/v1/loans/borrow");
    expect(options.method).toBe("POST");
    expect(JSON.parse(options.body)).toEqual({ member_id: "m1", book_id: "b1" });
  });

  it("includes due_at when provided", async () => {
    mockOk({ id: "loan-id", status: "BORROWED" });
    await loansApi.borrow({ member_id: "m1", book_id: "b1", due_at: "2025-12-01T00:00:00Z" });
    const body = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(body.due_at).toBe("2025-12-01T00:00:00Z");
  });
});

describe("loansApi.returnBook", () => {
  it("sends POST to /return with loan_id", async () => {
    mockOk({ id: "loan-id", status: "RETURNED", fine_amount: "0.00" });
    const result = await loansApi.returnBook({ loan_id: "loan-id" });
    expect(result.status).toBe("RETURNED");
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe("/api/v1/loans/return");
    expect(options.method).toBe("POST");
  });
});
