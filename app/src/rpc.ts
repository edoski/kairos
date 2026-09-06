import { createPublicClient, http } from "viem";
import type { Hash } from "viem";
import { avalanche, mainnet, polygon } from "viem/chains";

import type { BlockRow, Chain } from "./domain";
import type { PriorityFeeRewards } from "./features";

/**
 * Context prepared from one freshly observed head. Blocks are parent-linked;
 * reward rows align by height with the final manifest context and use wei per gas.
 */
export type PreparedChainContext = {
  blocks: readonly BlockRow[];
  priorityFeeRewards: readonly PriorityFeeRewards[];
};

export type ChainOutcome = {
  immediateBaseFeePerGas: bigint;
  selectedBaseFeePerGas: bigint;
};

export type ChainReader = {
  readContext(contextBlocks: number): Promise<PreparedChainContext>;
  readHead(): Promise<bigint>;
  readOutcome(
    immediateBlock: bigint,
    selectedBlock: bigint,
  ): Promise<ChainOutcome>;
};

type FetchedBlock = BlockRow & {
  hash: Hash;
  parentHash: Hash;
};

const CHAIN_DEFINITIONS = {
  ethereum: mainnet,
  polygon,
  avalanche,
} as const;

export function createChainReader(chain: Chain): ChainReader {
  const definition = CHAIN_DEFINITIONS[chain];
  const client = createPublicClient({
    chain: definition,
    cacheTime: 0,
    transport: http(undefined, {
      batch: chain === "polygon" ? { batchSize: 3 } : true,
      retryCount: 0,
    }),
  });

  async function readBlock(number: bigint): Promise<FetchedBlock> {
    const block = await client.getBlock({ blockNumber: number });
    if (block.baseFeePerGas === null || block.baseFeePerGas <= 0n) {
      throw new Error(
        `RPC returned block ${block.number} without a positive base fee`,
      );
    }
    return {
      number: block.number,
      timestamp: block.timestamp,
      baseFeePerGas: block.baseFeePerGas,
      gasUsed: block.gasUsed,
      gasLimit: block.gasLimit,
      transactionCount: block.transactions.length,
      hash: block.hash,
      parentHash: block.parentHash,
    };
  }

  async function readBlockRange(
    firstBlock: bigint,
    lastBlock: bigint,
  ): Promise<FetchedBlock[]> {
    return Promise.all(
      Array.from(
        { length: Number(lastBlock - firstBlock + 1n) },
        (_, offset) => readBlock(firstBlock + BigInt(offset)),
      ),
    );
  }

  async function readPriorityFeeRewards(
    head: bigint,
    firstBlock: bigint,
    contextBlocks: number,
  ): Promise<readonly PriorityFeeRewards[]> {
    const history = await client.getFeeHistory({
      blockCount: contextBlocks,
      blockNumber: head,
      rewardPercentiles: [50, 90],
    });
    if (history.oldestBlock !== firstBlock) {
      throw new Error(
        `Fee history must start at block ${firstBlock}, got ${history.oldestBlock}`,
      );
    }
    if (history.reward === undefined) {
      throw new Error("Fee history must include priority-fee rewards");
    }
    if (history.reward.length !== contextBlocks) {
      throw new Error(
        `Fee history must contain exactly ${contextBlocks} reward rows, got ${history.reward.length}`,
      );
    }
    return history.reward.map((rewards) => {
      const [p50, p90] = rewards;
      if (
        rewards.length !== 2 ||
        p50 < 0n ||
        p90 < 0n
      ) {
        throw new Error(
          "Fee history reward rows must contain nonnegative P50 and P90 values",
        );
      }
      return [p50, p90] as const;
    });
  }

  async function readContext(contextBlocks: number): Promise<PreparedChainContext> {
    const head = await client.getBlockNumber();
    const firstContextBlock = head - BigInt(contextBlocks) + 1n;
    const firstRawBlock = firstContextBlock - 1n;
    const [fetchedBlocks, priorityFeeRewards] = await Promise.all([
      readBlockRange(firstRawBlock, head),
      readPriorityFeeRewards(head, firstContextBlock, contextBlocks),
    ]);
    for (let index = 1; index < fetchedBlocks.length; index += 1) {
      const previous = fetchedBlocks[index - 1];
      const current = fetchedBlocks[index];
      if (current.parentHash !== previous.hash) {
        throw new Error(
          `Broken parent link between blocks ${previous.number} and ${current.number}`,
        );
      }
    }
    return {
      blocks: fetchedBlocks,
      priorityFeeRewards,
    };
  }

  function readHead(): Promise<bigint> {
    return client.getBlockNumber();
  }

  async function readOutcome(
    immediateBlock: bigint,
    selectedBlock: bigint,
  ): Promise<ChainOutcome> {
    const [immediate, selected] = await Promise.all([
      readBlock(immediateBlock),
      readBlock(selectedBlock),
    ]);
    return {
      immediateBaseFeePerGas: immediate.baseFeePerGas,
      selectedBaseFeePerGas: selected.baseFeePerGas,
    };
  }

  return {
    readContext,
    readHead,
    readOutcome,
  };
}
