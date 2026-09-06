import { useRef, useState, useSyncExternalStore } from "react";
import { StatusBar, StyleSheet, View } from "react-native";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";

import { BottomTabs, type AppTab } from "./src/components/BottomTabs";
import type { Chain, Horizon } from "./src/domain";
import { presentationError } from "./src/errors";
import { createRunHistory } from "./src/history";
import { currentHead, infer, resolveOutcome } from "./src/inference";
import { AnalyticsScreen } from "./src/screens/AnalyticsScreen";
import {
  InferenceScreen,
  type InferenceState,
} from "./src/screens/InferenceScreen";
import { colors } from "./src/theme";

type Selection = {
  chain: Chain;
  horizon: Horizon;
};

const INITIAL_SELECTION: Selection = {
  chain: "ethereum",
  horizon: 5,
};

export default function App() {
  const [tab, setTab] = useState<AppTab>("inference");
  const [selection, setSelection] = useState(INITIAL_SELECTION);
  const [inference, setInference] = useState<InferenceState>({
    status: "idle",
  });
  const [runHistory] = useState(createRunHistory);
  const { runs, storageError } = useSyncExternalStore(
    runHistory.subscribe,
    runHistory.getSnapshot,
  );
  const selectionRef = useRef<Selection>(INITIAL_SELECTION);
  const inferenceGeneration = useRef(0);

  function fail(message: string): void {
    setInference({ status: "error", message });
  }

  function select(next: Selection): void {
    const current = selectionRef.current;
    if (
      next.chain === current.chain &&
      next.horizon === current.horizon
    ) {
      return;
    }
    selectionRef.current = next;
    inferenceGeneration.current += 1;
    setSelection(next);
    setInference({ status: "idle" });
  }

  function selectChain(chain: Chain): void {
    select({ ...selectionRef.current, chain });
  }

  function selectHorizon(horizon: Horizon): void {
    select({ ...selectionRef.current, horizon });
  }

  /** Resolves pending runs for the chain captured when refresh begins. */
  async function refreshOutcomes(): Promise<void> {
    const chain = selectionRef.current.chain;
    const headBlock = await currentHead(chain);
    await runHistory.resolvePending(
      chain,
      headBlock,
      (immediateBlock, selectedBlock) =>
        resolveOutcome(chain, immediateBlock, selectedBlock),
    );
  }

  /**
   * Sends every completed inference to history; generation gates only
   * inference-state publication.
   */
  async function runInference() {
    const selected = selectionRef.current;
    inferenceGeneration.current += 1;
    const generation = inferenceGeneration.current;
    const isCurrent = () => inferenceGeneration.current === generation;

    setInference({ status: "loading" });
    let result;
    try {
      result = await infer(selected.chain, selected.horizon);
    } catch (error) {
      if (isCurrent()) {
        fail(presentationError(error));
      }
      return;
    }
    try {
      await runHistory.record(result);
    } catch {
      if (isCurrent()) {
        fail("Could not save this run.");
      }
      return;
    }
    if (isCurrent()) {
      setInference({ status: "success", result });
    }
  }

  return (
    <SafeAreaProvider>
      <StatusBar backgroundColor={colors.background} barStyle="dark-content" />
      <SafeAreaView edges={["top"]} style={styles.app}>
        <View style={styles.content}>
          {tab === "inference" ? (
            <InferenceScreen
              chain={selection.chain}
              horizon={selection.horizon}
              onChainChange={selectChain}
              onHorizonChange={selectHorizon}
              onRun={() => void runInference()}
              onReset={() => setInference({ status: "idle" })}
              state={inference}
            />
          ) : (
            <AnalyticsScreen
              key={selection.chain}
              chain={selection.chain}
              horizon={selection.horizon}
              onChainChange={selectChain}
              onHorizonChange={selectHorizon}
              onRefresh={refreshOutcomes}
              runs={runs}
              storageError={storageError}
            />
          )}
        </View>
        <SafeAreaView edges={["bottom"]} style={styles.tabSafeArea}>
          <BottomTabs onSelect={setTab} selected={tab} />
        </SafeAreaView>
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  app: { backgroundColor: colors.background, flex: 1 },
  content: { flex: 1 },
  tabSafeArea: { backgroundColor: colors.surface },
});
