import { render } from "@testing-library/react";
import { RouterProvider, createBrowserRouter } from "react-router";
import { describe, it } from "vitest";

import App from "./App";

describe("App", () => {
  it("renders without crashing", () => {
    render(
      <RouterProvider
        router={createBrowserRouter([{ path: "/", element: <App /> }])}
      ></RouterProvider>,
    );
  });
});
