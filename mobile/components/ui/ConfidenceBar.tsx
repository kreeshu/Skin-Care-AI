import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";

interface ConfidenceBarProps {
  label: string;
  confidence: number;
  /** Draws a tick where the score becomes "present". */
  threshold?: number;
  color?: string;
}

/** Dewy meter: mono label + soft petal track with rose fill. Data, not decoration. */
export function ConfidenceBar({
  label,
  confidence,
  threshold,
  color = colors.dispensary,
}: ConfidenceBarProps) {
  const safeConfidence = Number.isFinite(confidence) ? Math.min(1, Math.max(0, confidence)) : 0;
  const percentage = Math.round(safeConfidence * 100);

  return (
    <View style={styles.container}>
      <View style={styles.labelRow}>
        <Text style={styles.label}>{label}</Text>
        <Text style={[styles.percentage, { color }]}>{percentage}%</Text>
      </View>
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${percentage}%`, backgroundColor: color }]} />
        {threshold !== undefined && Number.isFinite(threshold) ? (
          <View style={[styles.tick, { left: `${Math.round(Math.min(1, Math.max(0, threshold)) * 100)}%` }]} />
        ) : null}
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
    height: 8,
    backgroundColor: colors.sage,
    borderRadius: 999,
    overflow: "hidden",
  },
  fill: {
    height: "100%",
    borderRadius: 999,
  },
  tick: {
    position: "absolute",
    top: 0,
    bottom: 0,
    width: 2,
    marginLeft: -1,
    backgroundColor: colors.textPrimary,
  },
});
