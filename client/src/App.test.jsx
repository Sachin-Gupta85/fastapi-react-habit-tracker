import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "./App.jsx";

describe("Habit Tracker App", () => {
  beforeEach(() => vi.restoreAllMocks());
  it("shows a habit with its streak", async () => {
    globalThis.fetch = vi.fn(() => Promise.resolve({
      ok: true, status: 200,
      json: async () => [{ id: "1", name: "Read", checkins: [], current_streak: 4, longest_streak: 7 }],
    }));
    render(<App />);
    await waitFor(() => expect(screen.getByText("Read")).toBeInTheDocument());
    expect(screen.getByText(/best 7/)).toBeInTheDocument();
  });
});
