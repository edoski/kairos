import { Ionicons } from "@expo/vector-icons";
import { Pressable, Text, View } from "react-native";

import { CHAINS, CHAIN_LABELS, type Chain } from "../domain";
import { styles } from "../styles";
import { colors } from "../theme";
import { NetworkIcon } from "./NetworkIcon";

export function NetworkChoices({
  chain,
  disabled,
  onChange,
}: {
  chain: Chain;
  disabled?: boolean;
  onChange: (chain: Chain) => void;
}) {
  return (
    <View style={styles.cardRow}>
      {CHAINS.map((choice) => {
        const active = choice === chain;
        return (
          <Pressable
            disabled={disabled}
            key={choice}
            onPress={() => onChange(choice)}
            style={[
              styles.networkCard,
              active && styles.networkCardActive,
            ]}
          >
            {active && (
              <Ionicons
                color={colors.blue}
                name="checkmark-circle"
                size={19}
                style={styles.check}
              />
            )}
            <NetworkIcon chain={choice} />
            <Text numberOfLines={1} style={styles.networkLabel}>
              {CHAIN_LABELS[choice]}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}
