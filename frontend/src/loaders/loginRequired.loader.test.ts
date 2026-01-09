import { redirect } from "react-router";
import { vi } from "vitest";
import { loginRequired } from "~/loaders/loginRequired.loader.ts";

vi.mock("react-router", () => ({
  redirect: vi.fn(),
}));

describe("loginRequired", () => {
  it("add a 403 handler to loader wrapped in `loginRequired`", async () => {
    const loader = () => {
      throw { status: 403 };
    };

    loginRequired(loader)({
      request: {
        url: "http://zaken.nl",
      } as unknown as Request,
      params: {},
      context: {},
      unstable_pattern: "",
    });
    expect(redirect).toHaveBeenCalledWith("/login?next=/");
  });

  it("should add the `next` query parameter", async () => {
    const loader = () => {
      throw { status: 403 };
    };

    loginRequired(loader)({
      request: {
        url: "http://zaken.nl/destruction-lists/",
      } as unknown as Request,
      params: {},
      context: {},
      unstable_pattern: "",
    });
    expect(redirect).toHaveBeenCalledWith("/login?next=/destruction-lists/");
  });

  it("should remove the `next` query parameter if set to prevent loops", async () => {
    const loader = () => {
      throw { status: 403 };
    };

    loginRequired(loader)({
      request: {
        url: "http://zaken.nl/?next=destruction-lists/",
      } as unknown as Request,
      params: {},
      context: {},
      unstable_pattern: "",
    });
    expect(redirect).toHaveBeenCalledWith("/login?next=/");
  });
});
