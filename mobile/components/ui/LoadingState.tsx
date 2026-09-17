import React, { useEffect, useState } from "react";
import { Animated, View, StyleSheet, ViewStyle } from "react-native";
import { colors } from "../../constants/colors";
import { theme, shadow } from "../../constants/theme";
import { Eyebrow } from "./Typography";

interface LoadingStateProps {
  eyebrow?: string;
  title?: string;
  rows?: number;
  style?: ViewStyle;
  /** Removes the title block; useful inside cards / list sections. */
  compact?: boolean;
}

/**
 * Skeleton list for data loading. Three soft sage rows pulse at the
 * same rate so the screen reads as "we're working" not "we froze".
 */
export function LoadingState({ eyebrow, title, rows = 3, style, compact = false }: LoadingStateProps) {
  const [opacity] = useState(() => new Animated.Value(0.45));

  useEffect(() => {
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, { toValue: 1, duration: 700, useNativeDriver: true }),
        Animated.timing(opacity, { toValue: 0.45, duration: 700, useNativeDriver: true }),
      ]),
    );
    loop.start();
    return () => loop.stop();
  }, [opacity]);

  return (
    <View style={[styles.container, compact && styles.compact, style]}>
      {eyebrow ? <Eyebrow>{eyebrow}</Eyebrow> : null}
      {title && !compact ? <View style={styles.titleBlock} /> : null}
      {Array.from({ length: rows }).map((_, i) => (
        <Animated.View key={i} style={[styles.row, { opacity }]} />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: theme.spacing.lg,
    gap: theme.spacing.md,
    backgroundColor: colors.paper,
  },
  compact: {
    flex: 0,
    paddingVertical: theme.spacing.md,
  },
  titleBlock: {
    height: 30,
    width: "60%",
    backgroundColor: colors.sage,
    borderRadius: theme.borderRadius.sm,
    marginBottom: theme.spacing.sm,
    ...shadow.hairline,
  },
  row: {
    height: 56,
    backgroundColor: colors.sage,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
  },
});
