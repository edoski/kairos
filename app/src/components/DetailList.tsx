import { Text, View } from "react-native";

import { styles } from "../styles";

export function DetailList({
  items,
}: {
  items: readonly (readonly [label: string, value: string])[];
}) {
  return items.map(([label, value], index) => (
    <View
      key={label}
      style={[
        styles.detailRow,
        index === items.length - 1 && styles.lastRow,
      ]}
    >
      <Text style={styles.detailLabel}>{label}</Text>
      <Text style={styles.detailValue}>{value}</Text>
    </View>
  ));
}
