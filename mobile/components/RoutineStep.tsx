import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors } from "../constants/colors";
import { theme } from "../constants/theme";

interface RoutineStepProps {
  step: number;
  title: string;
}

/** Step line: mono index + body text on a ruled line. Only numbered list in the app. */
export function RoutineStep({ step, title }: RoutineStepProps) {
  return (
    <View style={styles.container}>
      <Text style={styles.index}>{String(step).padStart(2, "0")}</Text>
      <Text style={styles.text}>{title}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    gap: 12,
    alignItems: "flex-start",
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: colors.line,
  },
  index: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    color: colors.textTertiary,
    marginTop: 3,
  },
  text: {
    flex: 1,
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.sm,
    color: colors.textPrimary,
    lineHeight: 20,
  },
});
