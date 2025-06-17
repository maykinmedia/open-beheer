// useCatalogi.test.tsx
import { renderHook, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import { getCatalogiChoices } from "~/api/catalogi.ts";

import { useCatalogi } from "./useCatalogi";

// Mock API
vi.mock("~/api/catalogi.ts", () => ({
  getCatalogiChoices: vi.fn(),
}));

describe("useCatalogi", () => {
  const mockService = { label: "Test Service", value: "test-service" };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("fetches catalogi choices when service is provided", async () => {
    const mockCatalogi = [
      { label: "Catalogus A", value: "cat-a" },
      { label: "Catalogus B", value: "cat-b" },
    ];
    (getCatalogiChoices as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      mockCatalogi,
    );

    const { result } = renderHook(() => useCatalogi(mockService));

    await waitFor(() => {
      expect(result.current.catalogiChoices.length).toBeGreaterThan(0);
    });

    expect(getCatalogiChoices).toHaveBeenCalledWith("test-service");
    expect(result.current.catalogiChoices).toEqual(mockCatalogi);
  });

  it("does not fetch catalogi when service is null", async () => {
    const { result } = renderHook(() => useCatalogi(null));

    await waitFor(() => {
      expect(result.current.catalogiChoices).toEqual([]);
    });

    expect(getCatalogiChoices).not.toHaveBeenCalled();
  });

  it("sets catalogiChoices to empty array if response is empty", async () => {
    (getCatalogiChoices as ReturnType<typeof vi.fn>).mockResolvedValueOnce([]);

    const { result } = renderHook(() => useCatalogi(mockService));

    await waitFor(() => {
      expect(result.current.catalogiChoices).toEqual([]);
    });
  });
});
