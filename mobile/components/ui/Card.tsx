import React from "react";
import { View, Text, StyleSheet, ViewStyle } from "react-native";
import { colors } from "../../constants/colors";
import { theme, shadow } from "../../constants/theme";

interface CardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  variant?: "default" | "elevated" | "outlined";
}

export function Card({ children, style, variant = "default" }: CardProps) {
  return <View style={[styles.card, styles[variant], style]}>{children}</View>;
}

/** Glow ticket: white sheet with pink veil border + soft rose lift. Only used for the analysis result. */
export function Ticket({ children, style }: { children: React.ReactNode; style?: ViewStyle }) {
  return <View style={[styles.card, styles.ticket, style]}>{children}</View>;
}

/** Pressed petal well for photo inputs and inactive surfaces. */
export function Well({ children, style }: { children: React.ReactNode; style?: ViewStyle }) {
  return <View style={[styles.well, style]}>{children}</View>;
}

/** Dashed perforation line used inside tickets. */
export function Perforation({ style }: { style?: ViewStyle }) {
  return <View style={[styles.perforation, style]} />;
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
    ...shadow.hairline,
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
    ...shadow.ticket,
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
    borderStyle: "dashed",
    marginVertical: theme.spacing.md,
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
    letterSpacing: 0,
  },
  subtitle: {
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.sm,
    letterSpacing: 0,
    color: colors.textSecondary,
    marginTop: theme.spacing.xs,
  },
});
