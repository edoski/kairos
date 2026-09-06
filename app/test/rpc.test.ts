import { afterEach, describe, expect, it, vi } from "vitest";
import type { Hash } from "viem";

import { createChainReader } from "../src/rpc";

type JsonRpcRequest = {
  id: number;
  method: string;
  params?: readonly unknown[];
};

type RpcFixture = {
  head: bigint;
  block(number: bigint): unknown;
  history(oldestBlock: bigint, count: number): unknown;
  batches: JsonRpcRequest[][];
};

function quantity(value: bigint): `0x${string}` {
  return `0x${value.toString(16)}`;
}

function hashOf(number: bigint): Hash {
  return `0x${number.toString(16).padStart(64, "0")}`;
}

function rpcBlock(
  number: bigint,
  overrides: {
    baseFeePerGas?: `0x${string}` | null;
    parentHash?: Hash;
  } = {},
) {
  return {
    number: quantity(number),
    hash: hashOf(number),
    parentHash: overrides.parentHash ?? hashOf(number - 1n),
    timestamp: quantity(1_700_000_000n + number),
    baseFeePerGas:
      overrides.baseFeePerGas === undefined
        ? quantity(1_000_000_000n + number)
        : overrides.baseFeePerGas,
    gasUsed: quantity(100n),
    gasLimit: quantity(200n),
    transactions: [],
  };
}

function feeHistory(oldestBlock: bigint, count: number) {
  return {
    oldestBlock: quantity(oldestBlock),
    baseFeePerGas: Array.from({ length: count + 1 }, (_, index) =>
      quantity(1_000_000_000n + BigInt(index)),
    ),
    gasUsedRatio: Array.from({ length: count }, () => 0.5),
    reward: Array.from({ length: count }, (_, index) => [
      quantity(2_000_000_000n + BigInt(index)),
      quantity(3_000_000_000n + BigInt(index)),
    ]),
  };
}

function installRpc(
  overrides: Partial<Pick<RpcFixture, "head" | "block" | "history">> = {},
): RpcFixture {
  const fixture: RpcFixture = {
    head: 12n,
    block: rpcBlock,
    history: feeHistory,
    batches: [],
    ...overrides,
  };
  vi.stubGlobal(
    "fetch",
    vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
      const parsed = JSON.parse(String(init?.body)) as
        | JsonRpcRequest
        | JsonRpcRequest[];
      const requests = Array.isArray(parsed) ? parsed : [parsed];
      fixture.batches.push(requests);
      const responses = requests.map((request) => ({
        jsonrpc: "2.0",
        id: request.id,
        result: rpcResult(fixture, request),
      }));
      return new Response(
        JSON.stringify(Array.isArray(parsed) ? responses : responses[0]),
        { headers: { "Content-Type": "application/json" } },
      );
    }),
  );
  return fixture;
}

function rpcResult(
  fixture: RpcFixture,
  request: JsonRpcRequest,
): unknown {
  if (request.method === "eth_blockNumber") {
    return quantity(fixture.head);
  }
  if (request.method === "eth_getBlockByNumber") {
    const tag = (request.params as readonly [string])[0];
    return fixture.block(BigInt(tag));
  }
  if (request.method === "eth_feeHistory") {
    const [countValue, headValue] = request.params as readonly [string, string];
    const count = Number(BigInt(countValue));
    const head = BigInt(headValue);
    return fixture.history(head - BigInt(count) + 1n, count);
  }
  throw new Error(`Unexpected RPC method: ${request.method}`);
}

function blockBatches(fixture: RpcFixture): bigint[][] {
  return fixture.batches
    .filter((batch) =>
      batch.some((request) => request.method === "eth_getBlockByNumber"),
    )
    .map((batch) =>
      batch
        .filter((request) => request.method === "eth_getBlockByNumber")
        .map((request) =>
          BigInt((request.params as readonly [string])[0]),
        ),
    );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("createChainReader", () => {
  it("reads exact ranges with one predecessor and aligned rewards", async () => {
    const rpc = installRpc();
    const reader = createChainReader("ethereum");

    const first = await reader.readContext(3);

    expect(first.blocks.map((block) => block.number)).toEqual([
      9n,
      10n,
      11n,
      12n,
    ]);
    expect(first.priorityFeeRewards).toEqual([
      [2_000_000_000n, 3_000_000_000n],
      [2_000_000_001n, 3_000_000_001n],
      [2_000_000_002n, 3_000_000_002n],
    ]);
    expect(blockBatches(rpc)).toEqual([
      [9n, 10n, 11n, 12n],
    ]);
    expect(
      rpc.batches
        .flat()
        .filter((request) => request.method === "eth_feeHistory")
        .map((request) => request.params),
    ).toEqual([
      ["0x3", "0xc", [50, 90]],
    ]);
  });

  it.each([
    {
      name: "fee history to start at the first context block",
      history: (oldestBlock: bigint, count: number) =>
        feeHistory(oldestBlock + 1n, count),
      message: "Fee history must start at block 10, got 11",
    },
    {
      name: "fee history to include priority-fee rewards",
      history: (oldestBlock: bigint, count: number) => ({
        ...feeHistory(oldestBlock, count),
        reward: undefined,
      }),
      message: "Fee history must include priority-fee rewards",
    },
    {
      name: "one priority-fee reward row per context block",
      history: (oldestBlock: bigint, count: number) => ({
        ...feeHistory(oldestBlock, count),
        reward: feeHistory(oldestBlock, count).reward.slice(1),
      }),
      message: "Fee history must contain exactly 3 reward rows, got 2",
    },
    {
      name: "each reward row to contain P50 and P90",
      history: (oldestBlock: bigint, count: number) => ({
        ...feeHistory(oldestBlock, count),
        reward: feeHistory(oldestBlock, count).reward.map((rewards, index) =>
          index === 0 ? rewards.slice(0, 1) : rewards,
        ),
      }),
      message:
        "Fee history reward rows must contain nonnegative P50 and P90 values",
    },
    {
      name: "priority-fee rewards to be nonnegative",
      history: (oldestBlock: bigint, count: number) => ({
        ...feeHistory(oldestBlock, count),
        reward: feeHistory(oldestBlock, count).reward.map(
          (rewards, index) =>
            index === 0 ? ["-1", rewards[1]] : rewards,
        ),
      }),
      message:
        "Fee history reward rows must contain nonnegative P50 and P90 values",
    },
  ])("requires $name", async ({ history, message }) => {
    const session = createChainReader("ethereum");
    installRpc({ history });

    await expect(session.readContext(3)).rejects.toThrow(message);
  });

  it("rejects a broken parent link in the fetched context", async () => {
    const rpc = installRpc({
      block: (number) =>
        rpcBlock(
          number,
          number === 11n ? { parentHash: hashOf(99n) } : {},
        ),
    });
    const session = createChainReader("ethereum");

    await expect(session.readContext(3)).rejects.toThrow(
      "Broken parent link between blocks 10 and 11",
    );
    expect(blockBatches(rpc)).toEqual([[9n, 10n, 11n, 12n]]);
  });

  it.each([null, quantity(0n)])(
    "rejects the nonpositive base fee %s",
    async (baseFeePerGas) => {
      installRpc({
        block: (number) =>
          rpcBlock(number, {
            baseFeePerGas:
              number === 12n ? baseFeePerGas : undefined,
          }),
      });
      const session = createChainReader("ethereum");

      await expect(session.readContext(1)).rejects.toThrow(
        "RPC returned block 12 without a positive base fee",
      );
    },
  );

  it("deduplicates an act-now block into one actual RPC observation", async () => {
    const rpc = installRpc();
    const session = createChainReader("ethereum");
    await expect(session.readOutcome(20n, 20n)).resolves.toEqual({
      immediateBaseFeePerGas: 1_000_000_020n,
      selectedBaseFeePerGas: 1_000_000_020n,
    });
    expect(blockBatches(rpc)).toEqual([[20n]]);
  });

  it("reads exact outcome blocks directly", async () => {
    const rpc = installRpc();
    const session = createChainReader("ethereum");

    await expect(session.readOutcome(20n, 22n)).resolves.toEqual({
      immediateBaseFeePerGas: 1_000_000_020n,
      selectedBaseFeePerGas: 1_000_000_022n,
    });
    expect(blockBatches(rpc)).toEqual([[20n, 22n]]);
  });
});
