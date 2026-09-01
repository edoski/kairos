import { createPublicClient, http } from "viem";
import type { GetBlockReturnType } from "viem";
import { avalanche, mainnet, polygon } from "viem/chains";

import type { BlockRow, Chain } from "./domain";
import {
  predecessorOffset,
  type ChainManifest,
  type PriorityFeeRewards,
} from "./features";

export type PreparedChainContext = {
  blocks: readonly BlockRow[];
  priorityFeeRewards: readonly PriorityFeeRewards[];
};

export type ChainOutcome = {
  immediateBaseFeePerGas: bigint;
  selectedBaseFeePerGas: bigint;
};

export type ChainSession = {
  sync(): Promise<PreparedChainContext>;
  readHead(): Promise<bigint>;
  readOutcome(
    immediateBlock: bigint,
    selectedBlock: bigint,
  ): Promise<ChainOutcome>;
};

const CHAIN_DEFINITIONS = {
  ethereum: mainnet,
  polygon,
  avalanche,
} as const;

export function createChainSession(
  chain: Chain,
  manifest: ChainManifest,
): ChainSession {
  const definition = CHAIN_DEFINITIONS[chain];
  const client = createPublicClient({
    chain: definition,
    cacheTime: 0,
    transport: http(undefined, {
      batch: true,
      retryCount: 0,
    }),
  });
  const offset = predecessorOffset(manifest);

  function blockRow(
    block: GetBlockReturnType<typeof definition, false, "latest">,
  ): BlockRow {
    return {
      number: block.number,
      timestamp: block.timestamp,
      baseFeePerGas: block.baseFeePerGas as bigint,
      gasUsed: block.gasUsed,
      gasLimit: block.gasLimit,
      transactionCount: block.transactions.length,
    };
  }

  async function readBlock(number: bigint): Promise<BlockRow> {
    return blockRow(await client.getBlock({ blockNumber: number }));
  }

  async function readBlockRange(
    firstBlock: bigint,
    lastBlock: bigint,
  ): Promise<BlockRow[]> {
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
  ): Promise<readonly PriorityFeeRewards[]> {
    const history = await client.getFeeHistory({
      blockCount: manifest.context_blocks,
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
    if (history.reward.length !== manifest.context_blocks) {
      throw new Error(
        `Fee history must contain exactly ${manifest.context_blocks} reward rows, got ${history.reward.length}`,
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

  async function sync(): Promise<PreparedChainContext> {
    const head = await client.getBlockNumber();
    const firstContextBlock =
      head - BigInt(manifest.context_blocks) + 1n;
    const firstRawBlock =
      firstContextBlock - BigInt(offset);
    const [blocks, priorityFeeRewards] = await Promise.all([
      readBlockRange(firstRawBlock, head),
      readPriorityFeeRewards(head, firstContextBlock),
    ]);
    return { blocks, priorityFeeRewards };
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
    sync,
    readHead,
    readOutcome,
  };
}
