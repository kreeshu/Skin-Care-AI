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

export function ConditionBadge({
  condition,
  confidence,
  size = "md",
}: ConditionBadgeProps) {
  const color = conditionColors[condition] || colors.textTertiary;

  return (
    <View
      style={[
        styles.badge,
        { backgroundColor: `${color}15`, borderColor: `${color}40` },
        size === "sm" && styles.sm,
        size === "lg" && styles.lg,
      ]}
    >
      <View style={[styles.dot, { backgroundColor: color }]} />
      <Text
        style={[
          styles.text,
          { color },
          size === "sm" && styles.textSm,
          size === "lg" && styles.textLg,
        ]}
      >
        {condition}
      </Text>
      {confidence !== undefined && (
        <Text
          style={[
            styles.confidence,
            { color },
            size === "sm" && styles.textSm,
          ]}
        >
          {" "}
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
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 100,
    borderWidth: 1,
    alignSelf: "flex-start",
  },
  sm: {
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  lg: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  text: {
    fontSize: theme.fontSize.sm,
    fontWeight: theme.fontWeight.semibold,
  },
  textSm: {
    fontSize: theme.fontSize.xs,
  },
  textLg: {
    fontSize: theme.fontSize.md,
  },
  confidence: {
    fontSize: theme.fontSize.sm,
    fontWeight: theme.fontWeight.bold,
  },
});
