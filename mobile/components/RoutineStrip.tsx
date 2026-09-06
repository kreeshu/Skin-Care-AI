import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors } from "../constants/colors";
import { theme } from "../constants/theme";

/**
 * Signature element: AM/PM daylight ribbon.
 * A two-column routine split by a peach-to-plum spine — order means something here.
 * Solid two-half spine, no gradient dep needed.
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
        <Text style={styles.columnLabel}>Morning · daylight</Text>
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
      <View style={styles.divider}>
        <View style={styles.dividerAm} />
        <View style={styles.dividerPm} />
      </View>
      <View style={styles.column}>
        <Text style={[styles.columnLabel, styles.pmLabel]}>Evening · night</Text>
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
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: 13,
    letterSpacing: 0,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  pmLabel: {
    color: colors.pine,
  },
  divider: {
    width: 3,
    borderRadius: 999,
    overflow: "hidden",
  },
  dividerAm: {
    flex: 1,
    backgroundColor: colors.amber,
  },
  dividerPm: {
    flex: 1,
    backgroundColor: colors.pine,
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
