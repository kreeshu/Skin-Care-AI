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

export function Badge({
  label,
  color = colors.white,
  backgroundColor = colors.primary,
  size = "md",
}: BadgeProps) {
  return (
    <View
      style={[
        styles.badge,
        { backgroundColor },
        size === "sm" && styles.sm,
      ]}
    >
      <Text style={[styles.text, { color }, size === "sm" && styles.textSm]}>
        {label}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 100,
    alignSelf: "flex-start",
  },
  sm: {
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  text: {
    fontSize: theme.fontSize.xs,
    fontWeight: theme.fontWeight.semibold,
  },
  textSm: {
    fontSize: 11,
  },
});
