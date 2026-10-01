import React from "react";
import { View, StyleSheet, ScrollView, TouchableOpacity } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Ticket, Perforation } from "../../components/ui/Card";
import { Eyebrow, DisplayHeading, DisplayLg, Body, BodySm, Caption } from "../../components/ui/Typography";
import { Badge } from "../../components/ui/Badge";
import { ConfidenceBar } from "../../components/ui/ConfidenceBar";
import { EmptyState } from "../../components/ui/EmptyState";
import { RoutineStrip } from "../../components/RoutineStrip";
import { RoutineStep } from "../../components/RoutineStep";
import { formatPrice } from "../../utils/format";
import { AnalysisResult, ProductRecommendation } from "../../types";

function ProductRecCard({ rec, onPress }: { rec: ProductRecommendation; onPress: () => void }) {
  return (
    <TouchableOpacity style={styles.recCard} onPress={onPress} activeOpacity={0.75} accessibilityRole="button">
      <View style={styles.recHeader}>
        <Body style={styles.recName} numberOfLines={1}>
          {rec.name}
        </Body>
        <Caption style={styles.recScore}>{rec.score.toFixed(2)}</Caption>
      </View>
      <BodySm style={styles.recFacts} numberOfLines={1}>
        {rec.brand} · {formatPrice(rec.discounted_price ?? rec.price)} ·{" "}
        {rec.rating ? `★ ${rec.rating.toFixed(1)}` : "No rating yet"}
      </BodySm>
      {rec.matching_ingredients.length > 0 ? (
        <BodySm style={styles.recIngredients} numberOfLines={1}>
          Fits · {rec.matching_ingredients.join(", ")}
        </BodySm>
      ) : null}
    </TouchableOpacity>
  );
}

/**
 * Heuristic AM/PM split when the SLM did not return a routine.
 * Known limitation: splits by count, not by step semantics. The SLM
 * path is preferred when available.
 */
function splitRoutineByCount(steps: string[]): { am: string[]; pm: string[] } {
  if (steps.length <= 1) return { am: steps, pm: [] };
  const half = Math.ceil(steps.length / 2);
  return { am: steps.slice(0, half), pm: steps.slice(half) };
}

export default function AnalysisScreen() {
  const params = useLocalSearchParams<{ id: string; result?: string }>();
  const router = useRouter();

  // Results always travel with the route (chat and history both pass them).
  const [result] = React.useState<AnalysisResult | null>(() => {
    if (!params.result) return null;
    try {
      return JSON.parse(params.result) as AnalysisResult;
    } catch {
      return null;
    }
  });
  if (!result) {
    return (
      <View style={styles.centered}>
        <EmptyState eyebrow="Not found" title="Result unavailable." message="Open it again from Chat or History." icon="search-outline" />
      </View>
    );
  }

  const strip =
    result.slm && (result.slm.routine.am.length > 0 || result.slm.routine.pm.length > 0)
      ? result.slm.routine
      : splitRoutineByCount(result.routine_suggestion || []);
  const present = result.concerns.filter((item) => item.status === "present");

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <Ticket>
        <Eyebrow>Your result</Eyebrow>
        <DisplayHeading style={styles.condition}>
          {present.length ? `${present.length} visible concern${present.length === 1 ? "" : "s"}` : "No visible concerns"}
        </DisplayHeading>
        <BodySm style={styles.readout}>
          {result.skin_type ? `Your skin type · ${result.skin_type}` : "Skin type not provided"}
        </BodySm>
        <View style={styles.meterGap}>
          {result.concerns.map((concern) => (
            <ConfidenceBar
              key={concern.name}
              label={`${concern.name.replace(/_/g, " ")} · ${concern.status}`}
              confidence={concern.score}
              threshold={concern.threshold}
            />
          ))}
        </View>

        <Perforation />

        <Body style={styles.sectionTitle}>Your routine</Body>
        <View style={styles.stripGap}>
          <RoutineStrip am={strip.am} pm={strip.pm} />
        </View>

        <BodySm style={styles.readout}>
          Bar = model score; tick = the threshold for that concern. Each concern has its own threshold, so compare a bar with its tick, not with other bars. Cosmetic observations, not diagnoses.
        </BodySm>
      </Ticket>

      <DisplayLg>{result.title}</DisplayLg>
      <Body style={styles.description}>{result.description}</Body>

      {result.recommendations && Object.keys(result.recommendations).length > 0 ? (
        <View>
          <Body style={styles.sectionTitle}>Why these fit</Body>
          {Object.entries(result.recommendations).map(([category, recs]) => (
            <View key={category} style={styles.section}>
              <View style={styles.sectionHead}>
                <Body style={styles.sectionName}>{category}</Body>
                <Caption>{recs.length} items</Caption>
              </View>
              {recs.slice(0, 3).map((rec) => (
                <ProductRecCard
                  key={rec.product_id}
                  rec={rec}
                  onPress={() => router.push(`/product/${rec.product_id}`)}
                />
              ))}
            </View>
          ))}
        </View>
      ) : null}

      {result.routine_suggestion.length > 0 && !(result.slm?.routine.am.length || result.slm?.routine.pm.length) ? (
        <View>
          <Body style={styles.sectionTitle}>Steps in order</Body>
          <View style={styles.section}>
            {result.routine_suggestion.map((step, idx) => (
              <RoutineStep key={idx} step={idx + 1} title={step} />
            ))}
          </View>
        </View>
      ) : null}

      <View style={styles.footnote}>
        <Badge label="Cosmetic only" size="sm" />
        <BodySm style={styles.footnoteText}>
          Not medical advice. See a dermatologist for medical concerns.
        </BodySm>
      </View>
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
    gap: theme.spacing.md,
  },
  centered: {
    flex: 1,
    backgroundColor: colors.background,
  },
  condition: {
    marginTop: theme.spacing.sm,
  },
  readout: {
    marginTop: theme.spacing.xs2,
    color: colors.textSecondary,
  },
  meterGap: {
    marginTop: theme.spacing.md,
  },
  stripGap: {
    marginTop: theme.spacing.sm,
  },
  description: {
    marginTop: -theme.spacing.sm,
    lineHeight: 23,
  },
  sectionTitle: {
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.md,
    color: colors.textPrimary,
    marginBottom: theme.spacing.sm,
  },
  section: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
  },
  sectionHead: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "baseline",
    marginBottom: theme.spacing.sm,
  },
  sectionName: {
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.sm,
    color: colors.textPrimary,
  },
  recCard: {
    paddingVertical: theme.spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.line,
  },
  recHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: theme.spacing.sm,
  },
  recName: {
    flex: 1,
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.sm,
  },
  recScore: {
    color: colors.dispensary,
  },
  recFacts: {
    marginTop: 3,
    color: colors.textSecondary,
  },
  recIngredients: {
    marginTop: 3,
  },
  footnote: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    padding: theme.spacing.md,
    backgroundColor: colors.sage,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
  },
  footnoteText: {
    flex: 1,
    lineHeight: 18,
  },
});
