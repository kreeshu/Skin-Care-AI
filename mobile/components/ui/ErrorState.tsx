import React from "react";
import { View, Text, StyleSheet, Platform } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Button } from "./Button";

interface ErrorStateProps {
  title: string;
  message: string;
  baseUrl?: string;
  icon?: keyof typeof Ionicons.glyphMap;
  onRetry: () => void;
  retryLabel?: string;
  compact?: boolean;
}

export function ErrorState({
  title,
  message,
  baseUrl,
  icon = "reader-outline",
  onRetry,
  retryLabel = "Retry",
  compact = false,
}: ErrorStateProps) {
  return (
    <View style={[styles.container, compact && styles.compact]}>
      <Text style={styles.eyebrow}>Dispensary note</Text>
      <View style={styles.iconWell}>
        <Ionicons name={icon} size={28} color={colors.pine} />
      </View>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.message}>{message}</Text>
      {baseUrl ? (
        <View style={styles.hintBox}>
          <Text style={styles.hintUrl} numberOfLines={1}>
            Server · {baseUrl}
          </Text>
          <Text style={styles.hint}>Start backend · python -m backend.run</Text>
          <Text style={styles.hint}>Health · {baseUrl}/api/health</Text>
        </View>
      ) : null}
      <Button title={retryLabel} onPress={onRetry} style={styles.retryButton} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: theme.spacing.lg,
    gap: 8,
    backgroundColor: colors.paper,
  },
  compact: {
    flex: 0,
    paddingVertical: theme.spacing.md,
  },
  eyebrow: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 1.2,
    textTransform: "uppercase" as const,
    color: colors.textSecondary,
  },
  iconWell: {
    width: 56,
    height: 56,
    borderRadius: 10,
    backgroundColor: colors.sage,
    borderWidth: 1,
    borderColor: colors.line,
    justifyContent: "center",
    alignItems: "center",
    marginVertical: theme.spacing.sm,
    ...Platform.select({
      web: {
        boxShadow: "0 1px 4px rgba(15,36,30,0.08)",
      } as any,
      default: {
        elevation: 1,
      },
    }),
  },
  title: {
    fontFamily: theme.fontFamily.display,
    fontSize: theme.fontSize.lg,
    color: colors.textPrimary,
    textAlign: "center",
    letterSpacing: -0.2,
  },
  message: {
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
    textAlign: "center",
    lineHeight: 20,
    maxWidth: 340,
  },
  hintBox: {
    marginTop: theme.spacing.sm,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    gap: 2,
    maxWidth: 340,
    width: "100%",
  },
  hintUrl: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 0.4,
    color: colors.textPrimary,
  },
  hint: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    color: colors.textSecondary,
  },
  retryButton: {
    marginTop: theme.spacing.md,
    minWidth: 160,
  },
});
