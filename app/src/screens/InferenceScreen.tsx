import { Ionicons } from "@expo/vector-icons";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  Text,
  View,
} from "react-native";

import { formatGwei } from "../analytics";
import { DetailRow } from "../components/DetailRow";
import { HorizonChoices } from "../components/HorizonChoices";
import { NetworkChoices } from "../components/NetworkChoices";
import { Overlay } from "../components/Overlay";
import { CHAIN_LABELS, type Chain, type Horizon } from "../domain";
import type { InferenceResult } from "../inference";
import { styles } from "../styles";
import { colors } from "../theme";

export type InferenceState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; result: InferenceResult }
  | { status: "error"; message: string };

type Props = {
  chain: Chain;
  horizon: Horizon;
  state: InferenceState;
  onChainChange: (chain: Chain) => void;
  onHorizonChange: (horizon: Horizon) => void;
  onRun: () => void;
  onRunAgain: () => void;
};

function ErrorDialog({
  message,
  onClose,
  onRetry,
}: {
  message: string;
  onClose: () => void;
  onRetry: () => void;
}) {
  return (
    <Overlay animationType="fade" centered onClose={onClose}>
      <View style={[styles.dialog, styles.errorDialog]}>
        <View style={styles.errorDialogIcon}>
          <Ionicons
            color={colors.red}
            name="alert-circle-outline"
            size={28}
          />
        </View>
        <Text style={styles.errorDialogTitle}>Inference failed</Text>
        <Text style={styles.errorDialogText}>{message}</Text>
        <View style={styles.errorActions}>
          <Pressable
            onPress={onClose}
            style={styles.dismissButton}
          >
            <Text style={styles.dismissButtonText}>Dismiss</Text>
          </Pressable>
          <Pressable
            onPress={onRetry}
            style={[styles.button, styles.retryButton]}
          >
            <Ionicons color={colors.surface} name="refresh" size={17} />
            <Text style={styles.buttonText}>Retry</Text>
          </Pressable>
        </View>
      </View>
    </Overlay>
  );
}

function Setup({
  horizon,
  state,
  onHorizonChange,
  onRun,
}: {
  horizon: Horizon;
  state: InferenceState;
  onHorizonChange: (horizon: Horizon) => void;
  onRun: () => void;
}) {
  const loading = state.status === "loading";
  return (
    <>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Horizon (K = {horizon})</Text>
        <HorizonChoices
          disabled={loading}
          onChange={onHorizonChange}
          value={horizon}
        />
      </View>

      <Pressable
        disabled={loading}
        onPress={onRun}
        style={[
          styles.button,
          styles.primaryButton,
          styles.setupButton,
          loading && styles.buttonDisabled,
        ]}
      >
        {loading && <ActivityIndicator color={colors.surface} />}
        <Text style={styles.buttonText}>
          {loading ? "Generating…" : "Get recommendation"}
        </Text>
      </Pressable>
    </>
  );
}

function Timeline({
  result,
}: {
  result: InferenceResult;
}) {
  return (
    <View style={styles.timeline}>
      <View style={[styles.timelineCell, styles.timelineHeadCell]}>
        <Text style={styles.timelineLabel}>Head</Text>
        <Text numberOfLines={1} style={styles.timelineBlock}>
          {result.head_block.toLocaleString()}
        </Text>
      </View>
      {Array.from({ length: result.K }, (_, offset) => {
        const active = offset === result.selected_action_k;
        return (
          <View
            key={offset}
            style={[styles.timelineCell, active && styles.timelineCellActive]}
          >
            <Text
              style={[
                styles.timelineOffset,
                active && styles.accentText,
              ]}
            >
              +{offset}
            </Text>
            <Ionicons
              color={active ? colors.teal : colors.muted}
              name={active ? "cube" : "cube-outline"}
              size={22}
            />
            <Text
              style={[
                styles.timelineTargetLabel,
                active && styles.accentText,
              ]}
            >
              {active ? "TARGET" : " "}
            </Text>
          </View>
        );
      })}
    </View>
  );
}

function Result({
  result,
  onRunAgain,
}: {
  result: InferenceResult;
  onRunAgain: () => void;
}) {
  const recommendation =
    result.selected_action_k === 0
      ? "Use the next block"
      : `Wait ${result.selected_action_k} ${result.selected_action_k === 1 ? "block" : "blocks"}`;
  return (
    <>
      <View style={[styles.surface, styles.recommendation]}>
        <View style={styles.successIcon}>
          <Ionicons color={colors.surface} name="checkmark" size={30} />
        </View>
        <View style={styles.recommendationCopy}>
          <Text style={styles.eyebrow}>Recommendation</Text>
          <Text style={styles.recommendationText}>{recommendation}</Text>
        </View>
      </View>

      <Timeline result={result} />

      <View style={[styles.surface, styles.detailsCard]}>
        <Text style={styles.detailsTitle}>Technical details</Text>
        <DetailRow label="Network" value={CHAIN_LABELS[result.chain]} />
        <DetailRow label="Horizon" value={`${result.K} blocks`} />
        <DetailRow
          label="Action offset"
          value={String(result.selected_action_k)}
        />
        <DetailRow
          label="Target block"
          value={result.target_block.toLocaleString()}
        />
        <DetailRow
          label="Predicted horizon minimum"
          last
          value={formatGwei(result.predicted_minimum_base_fee_per_gas)}
        />
      </View>

      <Pressable
        onPress={onRunAgain}
        style={[styles.button, styles.primaryButton]}
      >
        <Ionicons color={colors.surface} name="refresh" size={21} />
        <Text style={styles.buttonText}>Run again</Text>
      </Pressable>
    </>
  );
}

export function InferenceScreen(props: Props) {
  return (
    <>
      <ScrollView
        contentContainerStyle={styles.page}
        showsVerticalScrollIndicator={false}
      >
        <Text style={styles.title}>Inference</Text>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Network</Text>
          <NetworkChoices
            chain={props.chain}
            disabled={props.state.status === "loading"}
            onChange={props.onChainChange}
          />
        </View>
        {props.state.status === "success" ? (
          <Result
            onRunAgain={props.onRunAgain}
            result={props.state.result}
          />
        ) : (
          <Setup
            horizon={props.horizon}
            onHorizonChange={props.onHorizonChange}
            onRun={props.onRun}
            state={props.state}
          />
        )}
      </ScrollView>
      {props.state.status === "error" && (
        <ErrorDialog
          message={props.state.message}
          onClose={props.onRunAgain}
          onRetry={props.onRun}
        />
      )}
    </>
  );
}
