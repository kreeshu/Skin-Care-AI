import React from "react";
import { View, StyleSheet, ScrollView } from "react-native";
import { useLocalSearchParams } from "expo-router";
import { colors, conditionColor } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Badge } from "../../components/ui/Badge";
import { Eyebrow, DisplayHeading, Body, BodySm, Caption } from "../../components/ui/Typography";
import { ErrorState } from "../../components/ui/ErrorState";
import { EmptyState } from "../../components/ui/EmptyState";
import { LoadingState } from "../../components/ui/LoadingState";
import { RoutineStep } from "../../components/RoutineStep";
import { Condition } from "../../types";
import { api } from "../../services/api";
import { isApiError, toUserMessage } from "../../services/apiError";
import { useFetcher } from "../../hooks/useFetcher";

export default function ConditionDetailScreen() {
  const params = useLocalSearchParams<{ name: string }>();
  const { data: condition, loading, error, retry } = useFetcher<Condition>(
    () => api.getCondition(params.name || ""),
    [params.name],
  );

  if (loading) {
    return <LoadingState eyebrow="Guide · loading" rows={3} compact />;
  }

  if (error) {
    if (isApiError(error) && error.kind === "http" && error.status === 404) {
      return (
        <View style={styles.container}>
          <EmptyState
            eyebrow="Not found"
            title="No guide for this name."
            message="The name may be misspelled, or the guide isn't ready yet."
            icon="search-outline"
            actionLabel="Back to history"
          />
        </View>
      );
    }
    const { title, message } = toUserMessage(error);
    return (
      <View style={styles.container}>
        <ErrorState title={title} message={message} baseUrl={api.getBaseUrl()} onRetry={retry} />
      </View>
    );
  }

  if (!condition) {
    return (
      <View style={styles.container}>
        <EmptyState
          eyebrow="Not found"
          title="No guide for this name."
          icon="search-outline"
        />
      </View>
    );
  }

  const accent = conditionColor(condition.name);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <Eyebrow>Guide · {condition.is_medical ? "See a dermatologist" : "Common condition"}</Eyebrow>
      <DisplayHeading>{condition.title}</DisplayHeading>
      <View style={styles.rule}>
        <View style={[styles.tick, { backgroundColor: accent }]} />
        <Caption style={styles.ruleText}>{condition.name.toUpperCase()}</Caption>
      </View>

      <Body style={styles.description}>{condition.description}</Body>

      {condition.causes.length > 0 ? (
        <View style={styles.section}>
          <Body style={styles.sectionTitle}>Usual causes</Body>
          {condition.causes.map((cause, idx) => (
            <View key={idx} style={styles.line}>
              <BodySm>{cause}</BodySm>
            </View>
          ))}
        </View>
      ) : null}

      {condition.recommended_ingredients.length > 0 ? (
        <View style={styles.section}>
          <Body style={styles.sectionTitle}>Look for</Body>
          <View style={styles.tagRow}>
            {condition.recommended_ingredients.map((ing) => (
              <Badge key={ing} label={ing} size="sm" />
            ))}
          </View>
        </View>
      ) : null}

      {condition.recommended_categories.length > 0 ? (
        <View style={styles.section}>
          <Body style={styles.sectionTitle}>Shop by category</Body>
          <View style={styles.tagRow}>
            {condition.recommended_categories.map((cat) => (
              <Badge key={cat} label={cat} size="sm" />
            ))}
          </View>
        </View>
      ) : null}

      {condition.avoid_ingredients.length > 0 ? (
        <View style={[styles.section, styles.avoid]}>
          <Body style={styles.sectionTitle}>Skip these</Body>
          <View style={styles.tagRow}>
            {condition.avoid_ingredients.map((ing) => (
              <Badge key={ing} label={ing} size="sm" />
            ))}
          </View>
        </View>
      ) : null}

      {condition.tips.length > 0 ? (
        <View style={styles.section}>
          <Body style={styles.sectionTitle}>Daily care</Body>
          {condition.tips.map((tip, idx) => (
            <View key={idx} style={styles.line}>
              <BodySm>{tip}</BodySm>
            </View>
          ))}
        </View>
      ) : null}

      {condition.routine_steps.length > 0 ? (
        <View style={styles.section}>
          <Body style={styles.sectionTitle}>Steps in order</Body>
          {condition.routine_steps.map((step, idx) => (
            <RoutineStep key={idx} step={idx + 1} title={step} />
          ))}
        </View>
      ) : null}
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
    gap: theme.spacing.md - 4,
  },
  rule: {
    flexDirection: "row",
    alignItems: "center",
    gap: theme.spacing.sm,
  },
  tick: {
    width: 24,
    height: 3,
    borderRadius: 2,
  },
  ruleText: {
    color: colors.textSecondary,
  },
  description: {
    lineHeight: theme.lineHeight.body,
  },
  section: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    gap: theme.spacing.sm,
  },
  sectionTitle: {
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.md,
    color: colors.textPrimary,
  },
  avoid: {
    borderColor: colors.oxblood,
  },
  line: {
    paddingVertical: theme.spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.line,
  },
  tagRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: theme.spacing.xs2,
  },
});
