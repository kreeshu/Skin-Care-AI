import React from "react";
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
  TextStyle,
  Platform,
} from "react-native";
import { colors } from "../../constants/colors";
import { theme, shadow } from "../../constants/theme";

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: "primary" | "secondary" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  disabled?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  fullWidth?: boolean;
}

export function Button({
  title,
  onPress,
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  style,
  textStyle,
  fullWidth = false,
}: ButtonProps) {
  return (
    <TouchableOpacity
      accessibilityRole="button"
      accessibilityState={{ disabled: disabled || loading, busy: loading }}
      style={[
        styles.base,
        styles[variant],
        styles[`size_${size}`],
        disabled && styles.disabled,
        fullWidth && styles.fullWidth,
        style,
      ]}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.85}
    >
      {loading ? (
        <ActivityIndicator
          color={variant === "primary" ? colors.white : colors.dispensary}
          size="small"
        />
      ) : (
        <Text style={[styles.text, styles[`text_${variant}`], styles[`textSize_${size}`], textStyle]}>
          {title}
        </Text>
      )}
    </TouchableOpacity>
  );
}

const FOCUS_RING: ViewStyle = Platform.select({
  web: {
    outlineStyle: "solid",
    outlineWidth: 2,
    outlineOffset: 2,
    outlineColor: colors.dispensary,
  },
  default: {},
}) as ViewStyle;

const styles = StyleSheet.create({
  base: {
    borderRadius: theme.borderRadius.md,
    alignItems: "center",
    justifyContent: "center",
    flexDirection: "row",
    ...shadow.hairline,
    ...FOCUS_RING,
  },
  primary: {
    backgroundColor: colors.dispensary,
  },
  secondary: {
    backgroundColor: colors.sage,
  },
  outline: {
    backgroundColor: "transparent",
    borderWidth: 1,
    borderColor: colors.dispensary,
  },
  ghost: {
    backgroundColor: "transparent",
  },
  fullWidth: {
    alignSelf: "stretch",
  },
  size_sm: {
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.md,
  },
  size_md: {
    paddingVertical: theme.spacing.xs2 + 6, // 12
    paddingHorizontal: theme.spacing.lg,
  },
  size_lg: {
    paddingVertical: 15,
    paddingHorizontal: theme.spacing.xl,
  },
  disabled: {
    opacity: 0.5,
  },
  text: {
    fontFamily: theme.fontFamily.bodySemi,
    fontWeight: theme.fontWeight.semibold,
    letterSpacing: 0.2,
  },
  text_primary: {
    color: colors.white,
  },
  text_secondary: {
    color: colors.pine,
  },
  text_outline: {
    color: colors.dispensary,
  },
  text_ghost: {
    color: colors.dispensary,
  },
  textSize_sm: {
    fontSize: theme.fontSize.sm,
  },
  textSize_md: {
    fontSize: theme.fontSize.md,
  },
  textSize_lg: {
    fontSize: theme.fontSize.lg,
  },
});
