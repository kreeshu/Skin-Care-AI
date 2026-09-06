import React from "react";
import { View, Text, StyleSheet, ViewStyle } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../../constants/colors";
import { theme, shadow } from "../../constants/theme";
import { Button } from "./Button";
import { Eyebrow } from "./Typography";

interface EmptyStateProps {
  eyebrow?: string;
  title: string;
  message?: string;
  icon?: keyof typeof Ionicons.glyphMap;
  actionLabel?: string;
  onAction?: () => void;
  style?: ViewStyle;
  /** Removes flex:1 so the component sits inside cards / sections. */
  compact?: boolean;
}

/**
 * Zero-data state. Used on lists with no rows and on screens where
 * the user has not yet generated any data. Mirrors `ErrorState` so
 * the same place on the screen renders the right component.
 */
export function EmptyState({
  eyebrow = "No results",
  title,
  message,
  icon = "search-outline",
  actionLabel,
  onAction,
  style,
  compact = false,
}: EmptyStateProps) {
  return (
    <View style={[styles.container, compact && styles.compact, style]}>
      <Eyebrow>{eyebrow}</Eyebrow>
      <View style={styles.iconWell}>
        <Ionicons name={icon} size={26} color={colors.dispensary} />
      </View>
      <Text style={styles.title}>{title}</Text>
      {message ? <Text style={styles.message}>{message}</Text> : null}
      {actionLabel && onAction ? (
        <Button title={actionLabel} onPress={onAction} variant="outline" size="md" style={styles.action} />
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "flex-start",
    padding: theme.spacing.lg,
    gap: theme.spacing.sm,
    backgroundColor: colors.paper,
  },
  compact: {
    flex: 0,
    paddingVertical: theme.spacing.lg,
  },
  iconWell: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.sage,
    borderWidth: 1,
    borderColor: colors.line,
    justifyContent: "center",
    alignItems: "center",
    marginVertical: theme.spacing.sm,
    ...shadow.hairline,
  },
  title: {
    fontFamily: theme.fontFamily.display,
    fontSize: theme.fontSize.lg,
    color: colors.textPrimary,
    letterSpacing: -0.2,
  },
  message: {
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: theme.lineHeight.bodySm,
  },
  action: {
    marginTop: theme.spacing.md,
  },
});
