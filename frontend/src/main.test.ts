import * as ReactDOM from "react-dom/client";
import { Mock, expect, it, vi } from "vitest";

import "./main.tsx";

vi.mock("react-dom/client", async () => {
  const actual = await vi.importActual<typeof ReactDOM>("react-dom/client");
  return {
    ...actual,
    createRoot: vi.fn(() => ({
      render: vi.fn(),
    })),
  };
});

it("calls createRoot and renders App", () => {
  expect(ReactDOM.createRoot).toHaveBeenCalled();
  const renderFn = (ReactDOM.createRoot as Mock).mock.results[0].value.render;
  expect(renderFn).toHaveBeenCalled();
});
