/**
 * Component tests for BorrowForm.
 */

import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import BorrowForm from "@/components/loans/BorrowForm";

const mockSubmit = jest.fn();

beforeEach(() => mockSubmit.mockReset());

describe("BorrowForm", () => {
  it("renders member_id and book_id fields", () => {
    render(<BorrowForm onSubmit={mockSubmit} />);
    expect(screen.getByLabelText(/member id/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/book id/i)).toBeInTheDocument();
  });

  it("renders optional due date field", () => {
    render(<BorrowForm onSubmit={mockSubmit} />);
    expect(screen.getByLabelText(/due date/i)).toBeInTheDocument();
  });

  it("shows validation error when member_id is empty", async () => {
    render(<BorrowForm onSubmit={mockSubmit} />);
    fireEvent.click(screen.getByRole("button", { name: /borrow book/i }));
    await waitFor(() => {
      expect(screen.getByText(/member id is required/i)).toBeInTheDocument();
    });
    expect(mockSubmit).not.toHaveBeenCalled();
  });

  it("shows validation error when book_id is empty", async () => {
    render(<BorrowForm onSubmit={mockSubmit} />);
    await userEvent.type(screen.getByLabelText(/member id/i), "some-uuid");
    fireEvent.click(screen.getByRole("button", { name: /borrow book/i }));
    await waitFor(() => {
      expect(screen.getByText(/book id is required/i)).toBeInTheDocument();
    });
    expect(mockSubmit).not.toHaveBeenCalled();
  });

  it("calls onSubmit with valid data", async () => {
    mockSubmit.mockResolvedValue(undefined);
    render(<BorrowForm onSubmit={mockSubmit} />);

    await userEvent.type(screen.getByLabelText(/member id/i), "member-uuid-123");
    await userEvent.type(screen.getByLabelText(/book id/i), "book-uuid-456");
    fireEvent.click(screen.getByRole("button", { name: /borrow book/i }));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          member_id: "member-uuid-123",
          book_id: "book-uuid-456",
        }),
      );
    });
  });

  it("shows success message after successful submit", async () => {
    mockSubmit.mockResolvedValue(undefined);
    render(<BorrowForm onSubmit={mockSubmit} />);

    await userEvent.type(screen.getByLabelText(/member id/i), "m-uuid");
    await userEvent.type(screen.getByLabelText(/book id/i), "b-uuid");
    fireEvent.click(screen.getByRole("button", { name: /borrow book/i }));

    await waitFor(() => {
      expect(screen.getByText(/borrowed successfully/i)).toBeInTheDocument();
    });
  });

  it("shows error message on submit failure", async () => {
    mockSubmit.mockRejectedValue(new Error("No copies available"));
    render(<BorrowForm onSubmit={mockSubmit} />);

    await userEvent.type(screen.getByLabelText(/member id/i), "m-uuid");
    await userEvent.type(screen.getByLabelText(/book id/i), "b-uuid");
    fireEvent.click(screen.getByRole("button", { name: /borrow book/i }));

    await waitFor(() => {
      expect(screen.getByText(/no copies available/i)).toBeInTheDocument();
    });
  });
});
