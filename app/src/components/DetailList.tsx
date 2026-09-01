import { Text, View } from "react-native";

import { styles } from "../styles";

function DetailRow({
  label,
  value,
  last,
}: {
  label: string;
  value: string;
  last: boolean;
}) {
  return (
    <View style={[styles.detailRow, last && styles.lastRow]}>
      <Text style={styles.detailLabel}>{label}</Text>
      <Text style={styles.detailValue}>{value}</Text>
    </View>
  );
}

export function DetailList({
  items,
}: {
  items: readonly (readonly [label: string, value: string])[];
}) {
  return items.map(([label, value], index) => (
    <DetailRow
      key={label}
      label={label}
      last={index === items.length - 1}
      value={value}
    />
  ));
}
