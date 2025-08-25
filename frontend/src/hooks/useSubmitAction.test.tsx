import { Errors, useAlert } from "@maykin-ui/admin-ui";
import { act, renderHook } from "@testing-library/react";
import { useActionData, useSubmit } from "react-router";
import { Mock, beforeEach, describe, expect, it, vi } from "vitest";
import * as lib from "~/lib";

import { useSubmitAction } from "./useSubmitAction.tsx";

// Mocks
vi.mock("@maykin-ui/admin-ui", async (importOriginal) => {
  const actual = (await importOriginal()) as object;
  return {
    ...actual,
    useAlert: vi.fn(),
  };
});

vi.mock("react-router", async () => {
  const actual =
    await vi.importActual<typeof import("react-router")>("react-router");
  return {
    ...actual,
    useSubmit: vi.fn(),
    useActionData: vi.fn(),
  };
});

vi.mock("~/lib", () => ({
  collectErrorMessages: vi.fn(),
}));

describe("useSubmitAction", () => {
  let mockSubmit: ReturnType<typeof vi.fn>;
  let mockAlert: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockSubmit = vi.fn();
    (useSubmit as unknown as Mock).mockReturnValue(mockSubmit);

    mockAlert = vi.fn();
    (useAlert as unknown as Mock).mockReturnValue(mockAlert);

    (useActionData as unknown as Mock).mockReturnValue(undefined);
    (lib.collectErrorMessages as Mock).mockReturnValue([]);
  });

  it("should call submit with correct action and default options", () => {
    const { result } = renderHook(() => useSubmitAction());

    const action = { type: "TEST_ACTION", payload: { foo: "bar" } };

    act(() => {
      result.current(action);
    });

    expect(mockSubmit).toHaveBeenCalledWith(action, {
      method: "POST",
      encType: "application/json",
    });
  });

  it("should call submit with overridden options", () => {
    const { result } = renderHook(() => useSubmitAction());
    const action = { type: "TEST_ACTION", payload: 123 };

    act(() => {
      result.current(action, { method: "PUT" });
    });

    expect(mockSubmit).toHaveBeenCalledWith(
      action,
      expect.objectContaining({
        method: "PUT",
        encType: "application/json",
      }),
    );
  });

  it("should show alert when actionData contains errors", () => {
    const errors = "Something went wrong";
    (useActionData as unknown as Mock).mockReturnValue({
      field: ["Some error"],
    });
    (lib.collectErrorMessages as Mock).mockReturnValue(errors);

    renderHook(() => useSubmitAction());

    expect(mockAlert).toHaveBeenCalledWith(
      "Foutmelding",
      <Errors errors={errors} />,
      "Ok",
    );
  });

  it("should not show alert if catchErrors is false", () => {
    (useActionData as unknown as Mock).mockReturnValue({ error: "fail" });
    (lib.collectErrorMessages as Mock).mockReturnValue("fail");

    renderHook(() => useSubmitAction(false));

    expect(mockAlert).not.toHaveBeenCalled();
  });

  it("should not show alert if there are no errors", () => {
    (useActionData as unknown as Mock).mockReturnValue(undefined);
    renderHook(() => useSubmitAction());

    expect(mockAlert).not.toHaveBeenCalled();
  });
});
