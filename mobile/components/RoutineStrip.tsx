import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors } from "../constants/colors";
import { theme } from "../constants/theme";

/**
 * Signature element: AM/PM light strip.
 * A two-column routine split by a daylight divider — order means something here.
 */
export function RoutineStrip({
  am,
  pm,
}: {
  am: string[];
  pm: string[];
}) {
  return (
    <View style={styles.strip}>
      <View style={styles.column}>
        <Text style={styles.columnLabel}>AM · Daylight</Text>
        {am.length === 0 ? (
          <Text style={styles.empty}>No morning steps</Text>
        ) : (
          am.map((step, i) => (
            <View key={i} style={styles.doseLine}>
              <Text style={styles.doseIndex}>{String(i + 1).padStart(2, "0")}</Text>
              <Text style={styles.doseText}>{step}</Text>
            </View>
          ))
        )}
      </View>
      <View style={styles.divider} />
      <View style={styles.column}>
        <Text style={[styles.columnLabel, styles.pmLabel]}>PM · Night</Text>
        {pm.length === 0 ? (
          <Text style={styles.empty}>No evening steps</Text>
        ) : (
          pm.map((step, i) => (
            <View key={i} style={styles.doseLine}>
              <Text style={styles.doseIndex}>{String(i + 1).padStart(2, "0")}</Text>
              <Text style={styles.doseText}>{step}</Text>
            </View>
          ))
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  strip: {
    flexDirection: "row",
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    overflow: "hidden",
  },
  column: {
    flex: 1,
    padding: theme.spacing.md,
    gap: 8,
  },
  columnLabel: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 1,
    textTransform: "uppercase" as const,
    color: colors.amber,
    marginBottom: 4,
  },
  pmLabel: {
    color: colors.pine,
  },
  divider: {
    width: 2,
    backgroundColor: colors.amber,
    opacity: 0.55,
  },
  doseLine: {
    flexDirection: "row",
    gap: 8,
    alignItems: "flex-start",
  },
  doseIndex: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    color: colors.textTertiary,
    marginTop: 2,
  },
  doseText: {
    flex: 1,
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.sm,
    color: colors.textPrimary,
    lineHeight: 20,
  },
  empty: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    color: colors.textTertiary,
  },
});
