import { Platform, ViewStyle } from "react-native";
import { colors } from "./colors";

/**
 * Design tokens for Blush Apothecary. All screens and primitives
 * read spacing, radius, type, and shadow from here — never inline.
 */
export const theme = {
  colors,
  spacing: {
    hairline: 2,
    xs: 4,
    xs2: 6,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
    xxxl: 64,
  },
  borderRadius: {
    sm: 10,
    md: 16,
    lg: 20,
    xl: 28,
  },
  fontSize: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 24,
    xxl: 30,
    xxxl: 36,
  },
  lineHeight: {
    body: 23,
    bodySm: 20,
    bodyXs: 18,
    display: 34,
    displayLg: 38,
    displayXl: 44,
  },
  fontWeight: {
    regular: "400" as const,
    medium: "500" as const,
    semibold: "600" as const,
    bold: "700" as const,
  },
  fontFamily: {
    display: "Fraunces_600SemiBold",
    displayMedium: "Fraunces_500Medium",
    body: "Inter_400Regular",
    bodyTight: "InterTight_400Regular",
    bodyMedium: "Inter_500Medium",
    bodySemi: "Inter_600SemiBold",
    mono: "IBMPlexMono_500Medium",
  },
  letterSpacing: {
    monoEyebrow: 1.2,
    monoLabel: 0.8,
    monoTag: 0.6,
    tightDisplay: -0.5,
    displayLg: -0.3,
  },
} as const;

/**
 * Shadow tiers. Replaces the per-file `Platform.select({ web: { boxShadow } as any })`
 * pattern — typed once, reused everywhere.
 *
 *   hairline — single soft drop for raised cards
 *   ticket   — glow ticket lift
 *   card     — well / pressed surface
 *   raised   — modal or hero card
 */
export const shadow = {
  hairline: platformShadow("0 1px 4px rgba(219,39,119,0.08)", 1),
  ticket: platformShadow("0 2px 12px rgba(219,39,119,0.10)", 2),
  card: platformShadow("0 4px 18px rgba(219,39,119,0.10)", 3),
  raised: platformShadow("0 8px 28px rgba(219,39,119,0.14)", 6),
} as const;

function platformShadow(webBoxShadow: string, elevation: number): ViewStyle {
  return Platform.select({
    web: { boxShadow: webBoxShadow } as unknown as ViewStyle,
    default: { elevation },
  }) as ViewStyle;
}

export const eyebrows = {
  fontFamily: theme.fontFamily.mono,
  fontSize: 11,
  letterSpacing: theme.letterSpacing.monoEyebrow,
  textTransform: "uppercase" as const,
};
