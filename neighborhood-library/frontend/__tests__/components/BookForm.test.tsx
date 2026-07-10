/**
 * Component tests for BookForm.
 * Uses React Testing Library.
 */

import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import BookForm from "@/components/books/BookForm";

const mockSubmit = jest.fn();

beforeEach(() => {
  mockSubmit.mockReset();
});

describe("BookForm", () => {
  it("renders all required fields", () => {
    render(<BookForm onSubmit={mockSubmit} />);
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/author/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/isbn/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/year published/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/number of copies/i)).toBeInTheDocument();
  });

  it("shows validation error when title is empty on submit", async () => {
    render(<BookForm onSubmit={mockSubmit} />);
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
    });
    expect(mockSubmit).not.toHaveBeenCalled();
  });

  it("shows validation error when author is empty on submit", async () => {
    render(<BookForm onSubmit={mockSubmit} />);
    await userEvent.type(screen.getByLabelText(/title/i), "Test Title");
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(screen.getByText(/author is required/i)).toBeInTheDocument();
    });
    expect(mockSubmit).not.toHaveBeenCalled();
  });

  it("calls onSubmit with correct data when form is valid", async () => {
    mockSubmit.mockResolvedValue(undefined);
    render(<BookForm onSubmit={mockSubmit} />);

    await userEvent.type(screen.getByLabelText(/title/i), "Clean Code");
    await userEvent.type(screen.getByLabelText(/author/i), "Robert C. Martin");

    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith(
        expect.objectContaining({ title: "Clean Code", author: "Robert C. Martin" }),
      );
    });
  });

  it("renders cancel button when onCancel is provided", () => {
    const onCancel = jest.fn();
    render(<BookForm onSubmit={mockSubmit} onCancel={onCancel} />);
    expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument();
  });

  it("calls onCancel when cancel button is clicked", async () => {
    const onCancel = jest.fn();
    render(<BookForm onSubmit={mockSubmit} onCancel={onCancel} />);
    fireEvent.click(screen.getByRole("button", { name: /cancel/i }));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("shows submitLabel as button text", () => {
    render(<BookForm onSubmit={mockSubmit} submitLabel="Add Book" />);
    expect(screen.getByRole("button", { name: /add book/i })).toBeInTheDocument();
  });

  it("populates initial values from initial prop", () => {
    render(
      <BookForm
        onSubmit={mockSubmit}
        initial={{ title: "Prefilled Title", author: "Prefilled Author", copies_total: 5 }}
      />,
    );
    expect((screen.getByLabelText(/title/i) as HTMLInputElement).value).toBe("Prefilled Title");
    expect((screen.getByLabelText(/author/i) as HTMLInputElement).value).toBe("Prefilled Author");
  });

  it("shows error alert when onSubmit throws", async () => {
    mockSubmit.mockRejectedValue(new Error("Duplicate ISBN"));
    render(<BookForm onSubmit={mockSubmit} />);

    await userEvent.type(screen.getByLabelText(/title/i), "A");
    await userEvent.type(screen.getByLabelText(/author/i), "B");
    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(screen.getByText(/duplicate isbn/i)).toBeInTheDocument();
    });
  });
});
