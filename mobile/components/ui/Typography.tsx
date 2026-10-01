import React from "react";
import { Text, TextProps, TextStyle, StyleSheet } from "react-native";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";

/**
 * Typography primitives for Blush Apothecary.
 *
 * Use these on screen-level Text rather than re-declaring the same
 * fontFamily / fontSize / letterSpacing / color triplet inline.
 * Tokens live in `theme.fontSize`, `theme.lineHeight`, and
 * `theme.letterSpacing`.
 */

type Variant = "display" | "displayLg" | "title" | "subtitle" | "body" | "bodySm" | "caption" | "eyebrow" | "mono" | "monoTag";

interface TypographyProps extends TextProps {
  variant?: Variant;
  color?: string;
  align?: TextStyle["textAlign"];
  children: React.ReactNode;
}

export function Typography({ variant = "body", color, align, style, children, ...rest }: TypographyProps) {
  return (
    <Text style={[styles[variant], color ? { color } : null, align ? { textAlign: align } : null, style]} {...rest}>
      {children}
    </Text>
  );
}

/** Excon 30/34 tight — hero / scan / analysis headline. */
export function DisplayHeading({ children, style, ...rest }: TextProps) {
  return (
    <Text style={[styles.display, style]} {...rest}>
      {children}
    </Text>
  );
}

/** Excon 24/30 — section title in catalog / settings / history. */
export function DisplayLg({ children, style, ...rest }: TextProps) {
  return (
    <Text style={[styles.displayLg, style]} {...rest}>
      {children}
    </Text>
  );
}

/** Inter 16/23 — default body. */
export function Body({ children, style, ...rest }: TextProps) {
  return (
    <Text style={[styles.body, style]} {...rest}>
      {children}
    </Text>
  );
}

/** Inter 14/20 — secondary body. */
export function BodySm({ children, style, ...rest }: TextProps) {
  return (
    <Text style={[styles.bodySm, style]} {...rest}>
      {children}
    </Text>
  );
}

/** Mono 11/uppercase/tracked — small data labels. */
export function Caption({ children, style, ...rest }: TextProps) {
  return (
    <Text style={[styles.caption, style]} {...rest}>
      {children}
    </Text>
  );
}

/** Mono 11/uppercase/tracked wider — section eyebrow (SCAN / INDEX / MONOGRAPH). */
export function Eyebrow({ children, style, ...rest }: TextProps) {
  return (
    <Text style={[styles.eyebrow, style]} {...rest}>
      {children}
    </Text>
  );
}

const styles = StyleSheet.create({
  display: {
    fontFamily: theme.fontFamily.display,
    fontSize: theme.fontSize.xxl,
    lineHeight: theme.lineHeight.display,
    letterSpacing: theme.letterSpacing.tightDisplay,
    color: colors.textPrimary,
  },
  displayLg: {
    fontFamily: theme.fontFamily.display,
    fontSize: theme.fontSize.xl,
    lineHeight: theme.lineHeight.displayLg,
    letterSpacing: theme.letterSpacing.displayLg,
    color: colors.textPrimary,
  },
  title: {
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.md,
    lineHeight: theme.lineHeight.bodySm,
    color: colors.textPrimary,
  },
  subtitle: {
    fontFamily: theme.fontFamily.bodyMedium,
    fontSize: theme.fontSize.sm,
    lineHeight: theme.lineHeight.bodySm,
    color: colors.textSecondary,
  },
  body: {
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.md,
    lineHeight: theme.lineHeight.body,
    color: colors.textPrimary,
  },
  bodySm: {
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.sm,
    lineHeight: theme.lineHeight.bodySm,
    color: colors.textSecondary,
  },
  caption: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    lineHeight: theme.lineHeight.bodyXs,
    letterSpacing: theme.letterSpacing.monoTag,
    textTransform: "uppercase",
    color: colors.textSecondary,
  },
  eyebrow: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    lineHeight: theme.lineHeight.bodyXs,
    letterSpacing: theme.letterSpacing.monoEyebrow,
    textTransform: "uppercase",
    color: colors.textSecondary,
  },
  mono: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 12,
    color: colors.textPrimary,
  },
  monoTag: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 10,
    letterSpacing: theme.letterSpacing.monoTag,
    textTransform: "uppercase",
    color: colors.textTertiary,
  },
});
