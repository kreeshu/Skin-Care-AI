import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, ActivityIndicator } from "react-native";
import { useLocalSearchParams } from "expo-router";
import { colors, conditionColors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Badge } from "../../components/ui/Badge";
import { Eyebrow } from "../../components/ui/Card";
import { ErrorState } from "../../components/ui/ErrorState";
import { RoutineStep } from "../../components/RoutineStep";
import { Condition } from "../../types";
import { api } from "../../services/api";
import { isApiError, toUserMessage } from "../../services/apiError";

export default function ConditionDetailScreen() {
  const params = useLocalSearchParams<{ name: string }>();
  const [condition, setCondition] = useState<Condition | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);
  const [retryKey, setRetryKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = (await api.getCondition(params.name || "")) as Condition;
        if (!cancelled) setCondition(data);
      } catch (err) {
        console.error("Failed to load condition:", err);
        if (!cancelled) setError(err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [params.name, retryKey]);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.dispensary} />
      </View>
    );
  }

  if (error) {
    if (isApiError(error) && error.kind === "http" && error.status === 404) {
      return (
        <View style={styles.empty}>
          <Eyebrow>Monograph missing</Eyebrow>
          <Text style={styles.emptyTitle}>No entry for this name.</Text>
        </View>
      );
    }
    const { title, message } = toUserMessage(error);
    return (
      <ErrorState
        title={title}
        message={message}
        baseUrl={api.getBaseUrl()}
        onRetry={() => setRetryKey((k) => k + 1)}
      />
    );
  }

  if (!condition) {
    return (
      <View style={styles.empty}>
        <Eyebrow>Monograph missing</Eyebrow>
        <Text style={styles.emptyTitle}>No entry for this name.</Text>
      </View>
    );
  }

  const conditionColor = conditionColors[condition.name] || colors.textSecondary;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <Eyebrow>Monograph · {condition.is_medical ? "Flag for dermatologist" : "Common condition"}</Eyebrow>
      <Text style={styles.name}>{condition.title}</Text>
      <View style={styles.rule}>
        <View style={[styles.tick, { backgroundColor: conditionColor }]} />
        <Text style={styles.ruleText}>{condition.name.toUpperCase()}</Text>
      </View>

      <Text style={styles.description}>{condition.description}</Text>

      {condition.causes.length > 0 && (
        <View style={styles.section}>
          <Eyebrow>Usual causes</Eyebrow>
          {condition.causes.map((cause, idx) => (
            <View key={idx} style={styles.line}>
              <Text style={styles.lineText}>{cause}</Text>
            </View>
          ))}
        </View>
      )}

      {condition.recommended_ingredients.length > 0 && (
        <View style={styles.section}>
          <Eyebrow>Ask for</Eyebrow>
          <View style={styles.tagRow}>
            {condition.recommended_ingredients.map((ing) => (
              <Badge key={ing} label={ing} size="sm" />
            ))}
          </View>
        </View>
      )}

      {condition.recommended_categories.length > 0 && (
        <View style={styles.section}>
          <Eyebrow>Shop</Eyebrow>
          <View style={styles.tagRow}>
            {condition.recommended_categories.map((cat) => (
              <Badge key={cat} label={cat} size="sm" />
            ))}
          </View>
        </View>
      )}

      {condition.avoid_ingredients.length > 0 && (
        <View style={[styles.section, styles.avoid]}>
          <Eyebrow>Leave out</Eyebrow>
          <View style={styles.tagRow}>
            {condition.avoid_ingredients.map((ing) => (
              <Badge key={ing} label={ing} size="sm" />
            ))}
          </View>
        </View>
      )}

      {condition.tips.length > 0 && (
        <View style={styles.section}>
          <Eyebrow>Daily care</Eyebrow>
          {condition.tips.map((tip, idx) => (
            <View key={idx} style={styles.line}>
              <Text style={styles.lineText}>{tip}</Text>
            </View>
          ))}
        </View>
      )}

      {condition.routine_steps.length > 0 && (
        <View style={styles.section}>
          <Eyebrow>Steps in order</Eyebrow>
          {condition.routine_steps.map((step, idx) => (
            <RoutineStep key={idx} step={idx + 1} title={step} />
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: theme.spacing.md,
    paddingBottom: theme.spacing.xxl,
    gap: 12,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: colors.background,
  },
  name: {
    fontFamily: theme.fontFamily.display,
    fontSize: 30,
    letterSpacing: -0.5,
    color: colors.textPrimary,
    lineHeight: 34,
  },
  rule: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  tick: {
    width: 24,
    height: 3,
    borderRadius: 2,
  },
  ruleText: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 1,
    color: colors.textSecondary,
  },
  description: {
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.md,
    color: colors.textSecondary,
    lineHeight: 23,
  },
  section: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    gap: 8,
  },
  avoid: {
    borderColor: colors.oxblood,
  },
  line: {
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: colors.line,
  },
  lineText: {
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.sm,
    color: colors.textPrimary,
    lineHeight: 20,
  },
  tagRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
  },
  empty: {
    flex: 1,
    justifyContent: "center",
    alignItems: "flex-start",
    padding: theme.spacing.lg,
    gap: 8,
  },
  emptyTitle: {
    fontFamily: theme.fontFamily.display,
    fontSize: theme.fontSize.lg,
    color: colors.textPrimary,
  },
});
