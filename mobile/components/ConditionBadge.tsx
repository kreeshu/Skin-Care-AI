import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors } from "../constants/colors";
import { theme } from "../constants/theme";
import { conditionColors } from "../constants/colors";

interface ConditionBadgeProps {
  condition: string;
  confidence?: number;
  size?: "sm" | "md" | "lg";
}

export function ConditionBadge({ condition, confidence, size = "md" }: ConditionBadgeProps) {
  const color = conditionColors[condition] || colors.textSecondary;

  return (
    <View style={[styles.badge, size === "sm" && styles.sm, size === "lg" && styles.lg]}>
      <View style={[styles.tick, { backgroundColor: color }]} />
      <Text style={[styles.text, size === "sm" && styles.textSm, size === "lg" && styles.textLg]}>
        {condition.toUpperCase()}
      </Text>
      {confidence !== undefined && (
        <Text style={[styles.confidence, size === "sm" && styles.textSm]}>
          {"  "}
          {Math.round(confidence * 100)}%
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.surface,
    alignSelf: "flex-start",
  },
  sm: {
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  lg: {
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  tick: {
    width: 3,
    height: 14,
    borderRadius: 2,
    marginRight: 8,
  },
  text: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 12,
    letterSpacing: 0.8,
    color: colors.textPrimary,
  },
  textSm: {
    fontSize: 11,
  },
  textLg: {
    fontSize: 13,
  },
  confidence: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 12,
    color: colors.textSecondary,
  },
});
