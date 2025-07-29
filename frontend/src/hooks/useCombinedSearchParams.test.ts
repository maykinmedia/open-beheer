import { delay } from "@maykin-ui/client-common";
import { act, renderHook } from "@testing-library/react";
import { expect } from "vitest";

import { useCombinedSearchParams } from "./useCombinedSearchParams";

let state = new URLSearchParams();
const mockSetSearchParams = vi.fn((params: Record<string, string>) => {
  state = new URLSearchParams(params);
});

vi.mock("react-router", async () => {
  return {
    useSearchParams: vi.fn(() => {
      return [state, mockSetSearchParams];
    }),
  };
});

describe("useCombinedSearchParams", () => {
  beforeEach(() => {
    state = new URLSearchParams();
    mockSetSearchParams.mockClear();
  });

  it("updates params with existing ones", async () => {
    const { result } = renderHook(() => useCombinedSearchParams(0));

    act(() => {
      const [, setCombinedSearchParams] = result.current;
      setCombinedSearchParams({ foo: "bar" });
    });

    await delay(0);
    expect(Object.fromEntries(state)).toEqual({ foo: "bar" });
  });

  it("merges new params with existing ones", async () => {
    state = new URLSearchParams({ lorem: "ipsum" });
    const { result } = renderHook(() => useCombinedSearchParams(0));

    act(() => {
      const [, setCombinedSearchParams] = result.current;
      setCombinedSearchParams({ foo: "bar" });
    });

    await delay(0);
    expect(Object.fromEntries(state)).toEqual({ foo: "bar", lorem: "ipsum" });
  });

  it("debounces setSearchParams", async () => {
    state = new URLSearchParams({ lorem: "ipsum" });
    const { result } = renderHook(() => useCombinedSearchParams(100));

    await act(async () => {
      const [, setCombinedSearchParams] = result.current;
      setCombinedSearchParams({ foo: "bar" });
      setCombinedSearchParams({ foo: "bar" });
      await delay(100);
      setCombinedSearchParams({ foo: "bar" });
    });

    await delay(100);
    expect(mockSetSearchParams).toHaveBeenCalledTimes(2);
  });
});
