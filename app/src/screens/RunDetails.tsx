import { Ionicons } from "@expo/vector-icons";
import { Pressable, StyleSheet, Text, View } from "react-native";

import {
  formatGwei,
  formatRunDate,
  formatSavings,
  realizedSavingsPercent,
} from "../analytics";
import { DetailRow } from "../components/DetailRow";
import { Overlay } from "../components/Overlay";
import { CHAIN_LABELS } from "../domain";
import type { InferenceRun } from "../history";
import { styles as sharedStyles } from "../styles";
import { colors, radii } from "../theme";

export function RunDetails({
  run,
  onClose,
}: {
  run: InferenceRun;
  onClose: () => void;
}) {
  const savings = realizedSavingsPercent(run);
  return (
    <Overlay animationType="slide" onClose={onClose}>
      <View
        style={[
          sharedStyles.dialog,
          sharedStyles.sheet,
          styles.runDialog,
        ]}
      >
        <View style={styles.handle} />
        <View style={styles.dialogHeader}>
          <View>
            <Text style={styles.dialogTitle}>Run details</Text>
            <Text style={styles.dialogDate}>{formatRunDate(run.ran_at)}</Text>
          </View>
          <Pressable hitSlop={10} onPress={onClose}>
            <Ionicons color={colors.muted} name="close" size={27} />
          </Pressable>
        </View>

        <View style={styles.selectionSummary}>
          <View style={styles.selectionItem}>
            <Text style={sharedStyles.detailLabel}>Network</Text>
            <Text style={styles.detailStrong}>{CHAIN_LABELS[run.chain]}</Text>
          </View>
          <View style={styles.selectionItem}>
            <Text style={sharedStyles.detailLabel}>Horizon</Text>
            <Text style={styles.detailStrong}>{run.K} blocks</Text>
          </View>
        </View>

        <Text style={styles.groupTitle}>Prediction</Text>
        <View style={[sharedStyles.surface, sharedStyles.detailsCard]}>
          <DetailRow
            label="Head block"
            value={run.head_block.toLocaleString()}
          />
          <DetailRow
            label="Action offset"
            value={String(run.selected_action_k)}
          />
          <DetailRow
            label="Target block"
            value={run.target_block.toLocaleString()}
          />
          <DetailRow
            label="Predicted base fee"
            last
            value={formatGwei(run.predicted_minimum_base_fee_per_gas)}
          />
        </View>
        <Text style={styles.groupTitle}>Outcome</Text>
        <View style={[sharedStyles.surface, sharedStyles.detailsCard]}>
          <DetailRow
            label="Act-now base fee"
            value={
              run.outcome === undefined
                ? "Pending"
                : formatGwei(run.outcome.immediate_base_fee_per_gas)
            }
          />
          <DetailRow
            label="Selected base fee"
            value={
              run.outcome === undefined
                ? "Pending"
                : formatGwei(run.outcome.selected_base_fee_per_gas)
            }
          />
          <DetailRow
            label="Realized savings"
            last
            value={savings === null ? "Pending" : formatSavings(savings)}
          />
        </View>
        <Pressable
          onPress={onClose}
          style={[sharedStyles.button, styles.closeButton]}
        >
          <Text style={sharedStyles.buttonText}>Close</Text>
        </Pressable>
      </View>
    </Overlay>
  );
}

const styles = StyleSheet.create({
  runDialog: { paddingTop: 9 },
  handle: {
    alignSelf: "center",
    backgroundColor: colors.border,
    borderRadius: 3,
    height: 5,
    width: 48,
  },
  dialogHeader: {
    alignItems: "flex-start",
    flexDirection: "row",
    justifyContent: "space-between",
  },
  dialogTitle: { color: colors.ink, fontSize: 24, fontWeight: "800" },
  dialogDate: { color: colors.muted, fontSize: 13, marginTop: 2 },
  selectionSummary: {
    backgroundColor: colors.background,
    borderColor: colors.border,
    borderRadius: radii.medium,
    borderWidth: 1,
    flexDirection: "row",
    padding: 12,
  },
  selectionItem: { flex: 1, gap: 3 },
  detailStrong: { color: colors.ink, fontSize: 14, fontWeight: "700" },
  groupTitle: { color: colors.blue, fontSize: 15, fontWeight: "700" },
  closeButton: { minHeight: 50 },
});
