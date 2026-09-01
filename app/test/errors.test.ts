import { describe, expect, it } from "vitest";
import { BaseError } from "viem";

import { presentationError } from "../src/errors";

describe("presentationError", () => {
  it("uses compact Viem transport text", () => {
    const error = new BaseError("RPC request failed", {
      details: "HTTP body and transport details",
      docsPath: "/docs/errors",
    });

    expect(presentationError(error)).toBe("RPC request failed");
  });

  it.each([
    [new Error("Owner validation failed"), "Owner validation failed"],
    ["String rejection", "String rejection"],
    [null, "Unexpected error."],
    [{ reason: "unknown" }, "Unexpected error."],
  ])("maps %# to stable presentation text", (error, expected) => {
    expect(presentationError(error)).toBe(expected);
  });
});
