import { beforeEach, describe, expect, it, vi } from "vitest";
import { login } from "~/api/auth";
import { loginAction } from "~/pages";

vi.mock("~/api/auth", () => ({
  login: vi.fn(),
}));

vi.mock("react-router", async () => {
  const actual = await vi.importActual("react-router");
  return {
    ...actual,
    redirect: vi.fn((path: string) => ({ type: "redirect", location: path })),
  };
});

describe("loginAction", () => {
  const mockFormData = new FormData();
  const mockRequest = (url = "http://localhost/login") =>
    new Request(url, {
      method: "POST",
      body: mockFormData,
    });

  beforeEach(() => {
    mockFormData.set("username", "testuser");
    mockFormData.set("password", "testpass");
    vi.clearAllMocks();
  });

  it("calls login with correct arguments", async () => {
    (login as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({});

    await loginAction({ request: mockRequest(), params: {}, context: {} });

    expect(login).toHaveBeenCalledWith(
      "testuser",
      "testpass",
      expect.any(AbortSignal),
    );
  });

  it("redirects to '/' by default after successful login", async () => {
    (login as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({});

    const result = await loginAction({
      request: mockRequest(),
      params: {},
      context: {},
    });

    expect(result).toEqual({ type: "redirect", location: "/" });
  });

  it("redirects to 'next' query param if present", async () => {
    (login as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({});

    const result = await loginAction({
      request: mockRequest("http://localhost/login?next=/dashboard"),
      params: {},
      context: {},
    });

    expect(result).toEqual({ type: "redirect", location: "/dashboard" });
  });

  it("returns error JSON if login fails", async () => {
    const mockErrorResponse = new Response(
      JSON.stringify({ error: "Invalid credentials" }),
      {
        status: 401,
        headers: { "Content-Type": "application/json" },
      },
    );

    (login as unknown as ReturnType<typeof vi.fn>).mockImplementationOnce(
      () => {
        throw mockErrorResponse;
      },
    );

    const result = await loginAction({
      request: mockRequest(),
      params: {},
      context: {},
    });

    expect(result).toEqual({ error: "Invalid credentials" });
  });
});
