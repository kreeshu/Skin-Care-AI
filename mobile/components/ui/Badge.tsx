import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";

interface BadgeProps {
  label: string;
  color?: string;
  backgroundColor?: string;
  size?: "sm" | "md";
}

/** Soft pill tag for categories, skin types, concerns. Mono stays — it's data, not a heading. */
export function Badge({
  label,
  color = colors.pine,
  backgroundColor = colors.sage,
  size = "md",
}: BadgeProps) {
  return (
    <View style={[styles.badge, { backgroundColor, borderColor: backgroundColor }, size === "sm" && styles.sm]}>
      <Text style={[styles.text, { color }, size === "sm" && styles.textSm]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 999,
    alignSelf: "flex-start",
    borderWidth: 1,
    borderColor: colors.line,
  },
  sm: {
    paddingHorizontal: 6,
    paddingVertical: 3,
  },
  text: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 0.6,
    textTransform: "uppercase" as const,
    fontWeight: theme.fontWeight.medium,
  },
  textSm: {
    fontSize: 10,
  },
});
