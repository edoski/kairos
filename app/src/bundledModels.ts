import type { Chain, Horizon } from "./domain";
import type { ChainManifest } from "./features";

type TargetManifest = {
  mean: number;
  standard_deviation: number;
};

type ModelManifest = {
  target: TargetManifest;
};

type MobileChainManifest = ChainManifest & {
  models: Record<Horizon, ModelManifest>;
};

export type ModelSelection = {
  K: Horizon;
  source: number;
  chainManifest: MobileChainManifest;
  modelManifest: ModelManifest;
};

type MobileManifest = { chains: Record<Chain, MobileChainManifest> };
const manifest = require("../assets/models/manifest.json") as MobileManifest;
const resources = {
  ethereum: {
    2: require("../assets/models/ethereum-k2.pte"),
    3: require("../assets/models/ethereum-k3.pte"),
    4: require("../assets/models/ethereum-k4.pte"),
    5: require("../assets/models/ethereum-k5.pte"),
  },
  polygon: {
    2: require("../assets/models/polygon-k2.pte"),
    3: require("../assets/models/polygon-k3.pte"),
    4: require("../assets/models/polygon-k4.pte"),
    5: require("../assets/models/polygon-k5.pte"),
  },
  avalanche: {
    2: require("../assets/models/avalanche-k2.pte"),
    3: require("../assets/models/avalanche-k3.pte"),
    4: require("../assets/models/avalanche-k4.pte"),
    5: require("../assets/models/avalanche-k5.pte"),
  },
};

export function selectModel(chain: Chain, K: Horizon): ModelSelection {
  return {
    K,
    source: resources[chain][K],
    chainManifest: manifest.chains[chain],
    modelManifest: manifest.chains[chain].models[K],
  };
}
