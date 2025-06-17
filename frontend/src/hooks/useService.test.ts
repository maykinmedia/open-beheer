// useService.test.tsx
import { renderHook, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import { getServiceChoices } from "~/api/service.ts";

import { useService } from "./useService";

vi.mock("~/api/service.ts", () => ({
  getServiceChoices: vi.fn(),
}));

describe("useService", () => {
  it("fetches service choices and sets the first one as selected", async () => {
    const mockServices = [
      { label: "Service A", value: "service-a" },
      { label: "Service B", value: "service-b" },
    ];
    (getServiceChoices as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      mockServices,
    );

    const { result } = renderHook(() => useService());

    await waitFor(() => {
      expect(result.current.services.length).toBeGreaterThan(0);
    });

    expect(getServiceChoices).toHaveBeenCalled();
    expect(result.current.services).toEqual(mockServices);
    expect(result.current.service).toEqual(mockServices[0]);
  });

  it("sets service to null if no services are returned", async () => {
    (getServiceChoices as ReturnType<typeof vi.fn>).mockResolvedValueOnce([]);

    const { result } = renderHook(() => useService());

    await waitFor(() => {
      expect(result.current.services).toEqual([]);
    });

    expect(result.current.service).toBeNull();
  });
});
