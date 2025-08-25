import { describe, expect, it } from "vitest";
import { collectErrorMessages } from "~/lib";

describe("collectErrors", () => {
  it("should return array when join is undefined", () => {
    const error = "Something went wrong";
    const result = collectErrorMessages(error);
    expect(result).toEqual(["Something went wrong"]);
  });

  it("should return array when join is false", () => {
    const error = "Something went wrong";
    const result = collectErrorMessages(error, false);
    expect(result).toEqual(["Something went wrong"]);
  });

  it("should return string when join is true", () => {
    const error = ["Something went wrong", "Whoops"];
    const result = collectErrorMessages(error, true);
    expect(result).toEqual("Something went wrong\nWhoops");
  });

  it("should find nested errors", () => {
    const error = {
      nonFieldErrors: ["Unable to log in with provided credentials."],
      username: ["This field is required"],
      password: {
        error: "This field is required",
      },
    };
    const result = collectErrorMessages(error);
    expect(result).toEqual([
      "Unable to log in with provided credentials.",
      "This field is required",
      "This field is required",
    ]);
  });

  it("should filter `key` and `code` fields", () => {
    const error = {
      key: "foo",
      code: "bar",
      username: ["This field is required"],
    };
    const result = collectErrorMessages(error);
    expect(result).toEqual(["This field is required"]);
  });
});
