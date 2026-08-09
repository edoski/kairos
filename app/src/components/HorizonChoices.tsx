import { Pressable, Text, View } from "react-native";

import { HORIZONS, type Horizon } from "../domain";
import { styles } from "../styles";

export function HorizonChoices({
  disabled,
  onChange,
  value,
}: {
  disabled?: boolean;
  onChange: (value: Horizon) => void;
  value: Horizon;
}) {
  return (
    <View style={styles.cardRow}>
      {HORIZONS.map((choice) => {
        const active = choice === value;
        return (
          <Pressable
            disabled={disabled}
            key={choice}
            onPress={() => onChange(choice)}
            style={[
              styles.horizonChoice,
              active && styles.horizonChoiceActive,
            ]}
          >
            <Text
              style={[
                styles.horizonChoiceText,
                active && styles.horizonChoiceTextActive,
              ]}
            >
              K = {choice}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}
