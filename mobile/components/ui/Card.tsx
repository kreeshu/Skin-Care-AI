import React from "react";
import { View, Text, StyleSheet, ViewStyle, Platform } from "react-native";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";

interface CardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  variant?: "default" | "elevated" | "outlined";
}

export function Card({ children, style, variant = "default" }: CardProps) {
  return <View style={[styles.card, styles[variant], style]}>{children}</View>;
}

/** Prescription ticket: white sheet with hairline border + perforated divider. */
export function Ticket({ children, style }: { children: React.ReactNode; style?: ViewStyle }) {
  return <View style={[styles.card, styles.ticket, style]}>{children}</View>;
}

/** Pressed sage well for photo inputs and inactive surfaces. */
export function Well({ children, style }: { children: React.ReactNode; style?: ViewStyle }) {
  return <View style={[styles.well, style]}>{children}</View>;
}

/** Dashed perforation line used inside tickets. */
export function Perforation({ style }: { style?: ViewStyle }) {
  return <View style={[styles.perforation, style]} />;
}

/** Mono eyebrow label: SCAN / INDEX / PRESCRIPTION / LABEL / MONOGRAPH */
export function Eyebrow({ children, style }: { children: React.ReactNode; style?: any }) {
  return <Text style={[styles.eyebrow, style]}>{children}</Text>;
}

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  right?: React.ReactNode;
}

export function CardHeader({ title, subtitle, right }: CardHeaderProps) {
  return (
    <View style={styles.header}>
      <View style={styles.headerText}>
        <Text style={styles.title}>{title}</Text>
        {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
      </View>
      {right}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
  },
  default: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
  },
  elevated: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    ...Platform.select({
      web: {
        boxShadow: "0 1px 4px rgba(15,36,30,0.08)",
      } as any,
      default: {
        elevation: 1,
      },
    }),
  },
  outlined: {
    backgroundColor: "transparent",
    borderWidth: 1,
    borderColor: colors.line,
  },
  ticket: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    ...Platform.select({
      web: {
        boxShadow: "0 2px 10px rgba(15,36,30,0.08)",
      } as any,
      default: {
        elevation: 2,
      },
    }),
  },
  well: {
    backgroundColor: colors.sage,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: colors.line,
    padding: theme.spacing.md,
  },
  perforation: {
    borderTopWidth: 1,
    borderTopColor: colors.line,
    borderStyle: "dashed" as any,
    marginVertical: theme.spacing.md,
  },
  eyebrow: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: theme.letterSpacing.monoEyebrow,
    textTransform: "uppercase" as const,
    color: colors.textSecondary,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: theme.spacing.sm,
  },
  headerText: {
    flex: 1,
  },
  title: {
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.md,
    fontWeight: theme.fontWeight.semibold,
    color: colors.textPrimary,
    letterSpacing: 0.6,
    textTransform: "uppercase" as const,
  },
  subtitle: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 0.8,
    color: colors.textSecondary,
    marginTop: 4,
    textTransform: "uppercase" as const,
  },
});
