import { colors } from "./colors";

export const theme = {
  colors,
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  borderRadius: {
    sm: 8,
    md: 10,
    lg: 14,
    xl: 20,
  },
  fontSize: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 24,
    xxl: 30,
  },
  fontWeight: {
    regular: "400" as const,
    medium: "500" as const,
    semibold: "600" as const,
    bold: "700" as const,
  },
  fontFamily: {
    display: "Fraunces_600SemiBold",
    body: "Inter_400Regular",
    bodyMedium: "Inter_500Medium",
    bodySemi: "Inter_600SemiBold",
    mono: "IBMPlexMono_500Medium",
  },
  letterSpacing: {
    monoEyebrow: 1.2,
    tightDisplay: -0.5,
  },
};

export const eyebrows = {
  fontFamily: theme.fontFamily.mono,
  fontSize: 11,
  letterSpacing: theme.letterSpacing.monoEyebrow,
  textTransform: "uppercase" as const,
};
