import { renderHook, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { vi } from "vitest";
import { getCatalogiChoices } from "~/api/catalogi.ts";

import { useCatalogi } from "./useCatalogi";

vi.mock("~/api/catalogi.ts", () => ({
  getCatalogiChoices: vi.fn(),
}));
const mockedGetCatalogiChoices = vi.mocked(getCatalogiChoices);

describe("useCatalogi", () => {
  const mockService = { label: "Test Service", value: "test-service" };

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <MemoryRouter>{children}</MemoryRouter>
  );

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("fetches catalogi choices when service is provided", async () => {
    const mockCatalogi = [
      { label: "Catalogus A", value: "cat-a" },
      { label: "Catalogus B", value: "cat-b" },
    ];
    mockedGetCatalogiChoices.mockResolvedValueOnce(mockCatalogi);

    const { result } = renderHook(() => useCatalogi(mockService), { wrapper });

    await waitFor(() => {
      expect(result.current.catalogiChoices.length).toBeGreaterThan(0);
    });

    expect(mockedGetCatalogiChoices).toHaveBeenCalled();
    expect(mockedGetCatalogiChoices.mock.calls[0][0]).toBe("test-service");
    expect(mockedGetCatalogiChoices.mock.calls[0][1]).toBeInstanceOf(
      AbortSignal,
    );
    expect(result.current.catalogiChoices).toEqual(mockCatalogi);
  });

  it("does not fetch catalogi when service is null", async () => {
    const { result } = renderHook(() => useCatalogi(null), { wrapper });

    await waitFor(() => {
      expect(result.current.catalogiChoices).toEqual([]);
    });

    expect(mockedGetCatalogiChoices).not.toHaveBeenCalled();
  });

  it("sets catalogiChoices to empty array if response is empty", async () => {
    (
      mockedGetCatalogiChoices as ReturnType<typeof vi.fn>
    ).mockResolvedValueOnce([]);

    const { result } = renderHook(() => useCatalogi(mockService), { wrapper });

    await waitFor(() => {
      expect(result.current.catalogiChoices).toEqual([]);
    });
  });
});
