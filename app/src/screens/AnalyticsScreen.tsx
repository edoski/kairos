import { Ionicons } from "@expo/vector-icons";
import { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  Text,
  View,
} from "react-native";

import {
  formatRunDate,
  formatSavings,
  realizedSavingsPercent,
  summarizeRuns,
  waitBuckets,
} from "../analytics";
import { HorizonChoices } from "../components/HorizonChoices";
import { NetworkChoices } from "../components/NetworkChoices";
import { type Chain, type Horizon } from "../domain";
import { presentationError } from "../errors";
import type { InferenceRun } from "../history";
import { styles } from "../styles";
import { colors } from "../theme";
import { AnalyticsCharts } from "./AnalyticsCharts";
import { RunDetails } from "./RunDetails";

function SummaryCard({
  format,
  value,
  label,
  accent = false,
}: {
  format: (value: number) => string;
  value: number | null;
  label: string;
  accent?: boolean;
}) {
  return (
    <View style={[styles.surface, styles.summaryCard]}>
      <Text style={[styles.summaryValue, accent && styles.accentText]}>
        {value === null ? "—" : format(value)}
      </Text>
      <Text numberOfLines={1} style={styles.summaryLabel}>
        {label}
      </Text>
    </View>
  );
}

function runSummary(run: InferenceRun): string {
  const wait =
    run.selected_action_k === 0
      ? "Act now"
      : `Wait ${run.selected_action_k} block${run.selected_action_k === 1 ? "" : "s"}`;
  const savings = realizedSavingsPercent(run);
  if (savings === null) {
    return `${wait} · Pending`;
  }
  const outcome =
    savings >= 0
      ? `Saved ${formatSavings(savings)}`
      : `${formatSavings(Math.abs(savings))} higher`;
  return `${wait} · ${outcome}`;
}

export function AnalyticsScreen({
  runs,
  chain,
  horizon,
  onChainChange,
  onHorizonChange,
  onRefresh,
  storageError,
}: {
  runs: readonly InferenceRun[];
  chain: Chain;
  horizon: Horizon;
  onChainChange: (chain: Chain) => void;
  onHorizonChange: (horizon: Horizon) => void;
  onRefresh: () => Promise<void>;
  storageError: string | null;
}) {
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [refreshState, setRefreshState] = useState<
    { status: "idle" | "loading" } | { status: "error"; message: string }
  >({ status: "idle" });
  const selectedRun = runs.find((run) => run.id === selectedRunId) ?? null;
  const graphRuns = runs.filter(
    (run) => run.chain === chain && run.K === horizon,
  );
  const buckets = waitBuckets(graphRuns, horizon);
  const summary = summarizeRuns(graphRuns);

  async function refreshOutcomes(): Promise<void> {
    setRefreshState({ status: "loading" });
    try {
      await onRefresh();
      setRefreshState({ status: "idle" });
    } catch (error) {
      setRefreshState({
        status: "error",
        message: presentationError(error),
      });
    }
  }

  return (
    <>
      <ScrollView
        contentContainerStyle={styles.page}
        showsVerticalScrollIndicator={false}
      >
        <Text style={styles.title}>Analytics</Text>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Network</Text>
          <NetworkChoices
            chain={chain}
            onChange={onChainChange}
          />
        </View>

        {storageError && (
          <View style={styles.errorBanner}>
            <Text style={styles.errorBannerText}>{storageError}</Text>
          </View>
        )}

        <Pressable
          disabled={refreshState.status === "loading"}
          onPress={() => void refreshOutcomes()}
          style={[
            styles.button,
            styles.refreshButton,
            refreshState.status === "loading" && styles.buttonDisabled,
          ]}
        >
          {refreshState.status === "loading" ? (
            <ActivityIndicator color={colors.surface} />
          ) : (
            <Ionicons color={colors.surface} name="refresh" size={18} />
          )}
          <Text style={styles.buttonText}>
            {refreshState.status === "loading"
              ? "Refreshing…"
              : "Refresh outcomes"}
          </Text>
        </Pressable>
        {refreshState.status === "error" && (
          <View style={styles.errorBanner}>
            <Text style={styles.errorBannerText}>
              {refreshState.message}
            </Text>
          </View>
        )}

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Summary</Text>
          <View style={styles.cardRow}>
            <SummaryCard
              accent
              format={formatSavings}
              label="Avg savings"
              value={summary.averageSavingsPercent}
            />
            <SummaryCard
              format={(value) => `${value.toFixed(0)}%`}
              label="Win rate"
              value={summary.winPercent}
            />
            <SummaryCard
              format={(value) => value.toFixed(1)}
              label="Avg wait (blocks)"
              value={summary.averageWait}
            />
          </View>
        </View>

        <View style={styles.graphSection}>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>
              Horizon (K = {horizon})
            </Text>
            <HorizonChoices
              onChange={onHorizonChange}
              value={horizon}
            />
          </View>
          {graphRuns.length > 0 && <AnalyticsCharts buckets={buckets} />}
        </View>

        <Text style={styles.sectionTitle}>Runs ({graphRuns.length})</Text>
        <View style={[styles.surface, styles.clippedCard]}>
          {graphRuns.length === 0 ? (
            <View style={styles.emptyRuns}>
              <Text style={styles.emptyRunsTitle}>No runs yet</Text>
              <Text style={styles.emptyRunsText}>
                No runs match this horizon.
              </Text>
            </View>
          ) : (
            <ScrollView
              nestedScrollEnabled
              showsVerticalScrollIndicator={graphRuns.length > 4}
              style={styles.runScroller}
            >
              {graphRuns.map((run, index) => (
                <Pressable
                  key={run.id}
                  onPress={() => setSelectedRunId(run.id)}
                  style={[
                    styles.runRow,
                    index === graphRuns.length - 1 && styles.lastRow,
                  ]}
                >
                  <View style={styles.runIcon}>
                    <Ionicons
                      color={colors.blue}
                      name="git-branch-outline"
                      size={22}
                    />
                  </View>
                  <View style={styles.runCopy}>
                    <Text style={styles.runDate}>
                      {formatRunDate(run.ran_at)}
                    </Text>
                    <Text numberOfLines={1} style={styles.runMeta}>
                      {runSummary(run)}
                    </Text>
                  </View>
                  <Ionicons
                    color={colors.muted}
                    name="chevron-forward"
                    size={21}
                  />
                </Pressable>
              ))}
            </ScrollView>
          )}
        </View>
      </ScrollView>

      {selectedRun !== null && (
        <RunDetails onClose={() => setSelectedRunId(null)} run={selectedRun} />
      )}
    </>
  );
}
