import { useEffect, useRef, useState } from "react";
import { StatusBar, StyleSheet, View } from "react-native";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";

import { BottomTabs, type AppTab } from "./src/components/BottomTabs";
import type { Chain, Horizon } from "./src/domain";
import {
  createRunHistory,
  type InferenceRun,
} from "./src/history";
import {
  createInferenceRuntime,
  type InferenceRuntime,
} from "./src/inference";
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
  const [runs, setRuns] = useState<readonly InferenceRun[]>(
    runHistory.runs,
  );
  const [storageError, setStorageError] = useState<string | null>(
    runHistory.storageError,
  );
  const activeRuntime = useRef<InferenceRuntime | null>(null);
  const selectionRef = useRef<Selection>(INITIAL_SELECTION);
  const inferenceGeneration = useRef(0);

  function fail(message: string): void {
    setInference({ status: "error", message });
  }

  useEffect(() => {
    return runHistory.subscribe(() => {
      setRuns(runHistory.runs);
      setStorageError(runHistory.storageError);
    });
  }, [runHistory]);

  useEffect(() => {
    const runtime = createInferenceRuntime();
    activeRuntime.current = runtime;

    return () => {
      if (activeRuntime.current === runtime) {
        activeRuntime.current = null;
      }
      void runtime.dispose().catch(() => {});
    };
  }, []);

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

  async function refreshOutcomes(): Promise<void> {
    const chain = selectionRef.current.chain;
    const runtime = activeRuntime.current;
    if (runtime === null) {
      throw new Error("Could not connect to the selected chain.");
    }
    const headBlock = await runtime.currentHead(chain);
    await runHistory.resolvePending(
      chain,
      headBlock,
      (immediateBlock, selectedBlock) =>
        runtime.resolveOutcome(chain, immediateBlock, selectedBlock),
    );
  }

  async function runInference() {
    const selected = selectionRef.current;
    inferenceGeneration.current += 1;
    const generation = inferenceGeneration.current;
    const runtime = activeRuntime.current;
    if (runtime === null) {
      fail("Could not connect to the selected chain.");
      return;
    }
    const isCurrent = () => inferenceGeneration.current === generation;

    setInference({ status: "loading" });
    let result;
    try {
      result = await runtime.run(selected.chain, selected.horizon);
    } catch (error) {
      if (isCurrent()) {
        fail(error instanceof Error ? error.message : String(error));
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
              onHorizonChange={(horizon) =>
                select({ ...selectionRef.current, horizon })
              }
              onRun={() => void runInference()}
              onRunAgain={() => setInference({ status: "idle" })}
              state={inference}
            />
          ) : (
            <AnalyticsScreen
              chain={selection.chain}
              horizon={selection.horizon}
              onChainChange={selectChain}
              onHorizonChange={(horizon) =>
                select({ ...selectionRef.current, horizon })
              }
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
