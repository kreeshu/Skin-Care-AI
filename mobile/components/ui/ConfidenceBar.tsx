import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";

interface ConfidenceBarProps {
  label: string;
  confidence: number;
  color?: string;
}

/** Lab readout: mono label + hairline meter, no gradient. */
export function ConfidenceBar({
  label,
  confidence,
  color = colors.dispensary,
}: ConfidenceBarProps) {
  const percentage = Math.round(confidence * 100);

  return (
    <View style={styles.container}>
      <View style={styles.labelRow}>
        <Text style={styles.label}>{label}</Text>
        <Text style={[styles.percentage, { color }]}>{percentage}%</Text>
      </View>
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${percentage}%`, backgroundColor: color }]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: theme.spacing.sm,
  },
  labelRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6,
  },
  label: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 0.8,
    textTransform: "uppercase" as const,
    color: colors.textSecondary,
  },
  percentage: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 12,
    fontWeight: theme.fontWeight.semibold,
  },
  track: {
    height: 4,
    backgroundColor: colors.sage,
    borderRadius: 2,
    overflow: "hidden",
  },
  fill: {
    height: "100%",
    borderRadius: 2,
  },
});
