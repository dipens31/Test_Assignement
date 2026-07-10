/**
 * Unit tests for the API client.
 * fetch is mocked at the module level.
 */

import { api, ApiClientError } from "@/lib/api/client";

const mockFetch = jest.fn();
global.fetch = mockFetch;

function mockResponse(status: number, body: unknown) {
  const text = JSON.stringify(body);
  mockFetch.mockResolvedValueOnce({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
    text: async () => text,
  });
}

describe("api.get", () => {
  afterEach(() => jest.clearAllMocks());

  it("returns parsed JSON on 200", async () => {
    mockResponse(200, { id: "abc", title: "Test" });
    const result = await api.get<{ id: string; title: string }>("/api/v1/books");
    expect(result).toEqual({ id: "abc", title: "Test" });
    const [, opts] = mockFetch.mock.calls[0];
    expect(opts.headers["Content-Type"]).toBe("application/json");
    expect(opts.method).toBeUndefined();
  });

  it("throws ApiClientError on 404", async () => {
    const make404 = () =>
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: "Book not found" }),
        text: async () => JSON.stringify({ detail: "Book not found" }),
      });
    make404();
    await expect(api.get("/api/v1/books/bad-id")).rejects.toThrow(ApiClientError);
    make404();
    await expect(api.get("/api/v1/books/bad-id")).rejects.toThrow("Book not found");
  });

  it("throws ApiClientError on 409 conflict", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 409,
      json: async () => ({ detail: "Already exists" }),
      text: async () => JSON.stringify({ detail: "Already exists" }),
    });
    try {
      await api.get("/api/v1/books/dup");
    } catch (e) {
      expect(e).toBeInstanceOf(ApiClientError);
      expect((e as ApiClientError).status).toBe(409);
    }
  });
});

describe("api.post", () => {
  afterEach(() => jest.clearAllMocks());

  it("sends POST with JSON body and returns result", async () => {
    const payload = { title: "New Book", author: "Author", copies_total: 1 };
    const response = { id: "uuid-123", ...payload, copies_available: 1 };
    mockResponse(201, response);

    const result = await api.post<typeof response>("/api/v1/books", payload);
    expect(result.id).toBe("uuid-123");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/books",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify(payload),
      }),
    );
  });

  it("includes Content-Type header", async () => {
    mockResponse(201, {});
    await api.post("/api/v1/books", {});
    const [, options] = mockFetch.mock.calls[0];
    expect(options.headers["Content-Type"]).toBe("application/json");
  });
});

describe("api.put", () => {
  afterEach(() => jest.clearAllMocks());

  it("sends PUT with correct method", async () => {
    mockResponse(200, { id: "uuid", title: "Updated" });
    await api.put("/api/v1/books/uuid", { title: "Updated" });
    const [, options] = mockFetch.mock.calls[0];
    expect(options.method).toBe("PUT");
  });
});
