import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { colors, conditionColors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Ticket, Perforation, Eyebrow } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { ConfidenceBar } from "../../components/ui/ConfidenceBar";
import { RoutineStrip } from "../../components/RoutineStrip";
import { RoutineStep } from "../../components/RoutineStep";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { AnalysisResult, ProductRecommendation } from "../../types";

function ProductRecCard({ rec, onPress }: { rec: ProductRecommendation; onPress: () => void }) {
  return (
    <TouchableOpacity style={styles.recCard} onPress={onPress} activeOpacity={0.75}>
      <View style={styles.recHeader}>
        <Text style={styles.recName} numberOfLines={1}>
          {rec.name}
        </Text>
        <Text style={styles.recScore}>{rec.score.toFixed(2)}</Text>
      </View>
      <Text style={styles.recFacts}>
        {rec.brand.toUpperCase()} · RS. {Math.round(rec.discounted_price || rec.price || 0).toLocaleString()} ·{" "}
        {rec.rating ? `★ ${rec.rating.toFixed(1)}` : "UNRATED"}
      </Text>
      {rec.matching_ingredients.length > 0 && (
        <Text style={styles.recIngredients} numberOfLines={1}>
          Fits · {rec.matching_ingredients.join(", ")}
        </Text>
      )}
    </TouchableOpacity>
  );
}

function splitRoutine(steps: string[]): { am: string[]; pm: string[] } {
  if (steps.length <= 1) return { am: steps, pm: [] };
  const half = Math.ceil(steps.length / 2);
  return { am: steps.slice(0, half), pm: steps.slice(half) };
}

export default function AnalysisScreen() {
  const params = useLocalSearchParams<{ id: string; result?: string }>();
  const router = useRouter();
  const [result, setResult] = useState<AnalysisResult | null>(null);

  useEffect(() => {
    if (params.result) {
      try {
        setResult(JSON.parse(params.result));
      } catch {}
    }
  }, [params.result]);

  if (!result) {
    return <LoadingSpinner />;
  }

  const conditionColor = conditionColors[result.detected_condition] || colors.textSecondary;
  const strip = result.slm && (result.slm.routine.am.length > 0 || result.slm.routine.pm.length > 0)
    ? result.slm.routine
    : splitRoutine(result.routine_suggestion || []);
  const isSerious = result.is_medical && result.detected_condition === "Carcinoma";

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <Ticket>
        <Eyebrow>Prescription · filed {String(params.id || "").slice(0, 8)}</Eyebrow>
        <Text style={styles.condition}>{result.detected_condition}</Text>
        <Text style={styles.readout}>
          {result.skin_type ? `${result.skin_type.toUpperCase()} ${Math.round(result.skin_type_confidence * 100)}%` : ""}{result.skin_type ? "  ·  " : ""}READING {Math.round(result.condition_confidence * 100)}%
        </Text>
        <View style={styles.meterGap}>
          <ConfidenceBar label="Reading confidence" confidence={result.condition_confidence} color={conditionColor} />
          {result.skin_type_confidence > 0 && (
            <ConfidenceBar label="Skin type" confidence={result.skin_type_confidence} />
          )}
        </View>

        <Perforation />

        <Eyebrow>Your routine</Eyebrow>
        <View style={styles.stripGap}>
          <RoutineStrip am={strip.am} pm={strip.pm} />
        </View>

        {isSerious && (
          <View style={styles.serious}>
            <Ionicons name="alert-circle" size={18} color={colors.oxblood} />
            <Text style={styles.seriousText}>
              This reading needs a dermatologist promptly. This app does not diagnose.
            </Text>
          </View>
        )}
      </Ticket>

      <Text style={styles.title}>{result.title}</Text>
      <Text style={styles.description}>{result.description}</Text>

      {result.recommendations && Object.keys(result.recommendations).length > 0 && (
        <>
          <Eyebrow>Why these fit</Eyebrow>
          {Object.entries(result.recommendations).map(([category, recs]) => (
            <View key={category} style={styles.section}>
              <View style={styles.sectionHead}>
                <Text style={styles.sectionName}>{category}</Text>
                <Text style={styles.sectionCount}>{recs.length} items</Text>
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
        </>
      )}

      {result.slm && (
        <>
          <Eyebrow>Dispenser notes</Eyebrow>
          <View style={styles.section}>
            {result.slm.chosen.map((item, idx) => (
              <View key={idx} style={styles.slmItem}>
                <Text style={styles.slmName}>{item.name}</Text>
                <Text style={styles.slmCategory}>{item.category}</Text>
                <Text style={styles.slmReason}>{item.reason}</Text>
              </View>
            ))}
          </View>
        </>
      )}

      {result.routine_suggestion.length > 0 && !(result.slm?.routine.am.length || result.slm?.routine.pm.length) && (
        <>
          <Eyebrow>Steps in order</Eyebrow>
          <View style={styles.section}>
            {result.routine_suggestion.map((step, idx) => (
              <RoutineStep key={idx} step={idx + 1} title={step} />
            ))}
          </View>
        </>
      )}

      <View style={styles.footnote}>
        <Badge label="Cosmetic only" size="sm" />
        <Text style={styles.footnoteText}>
          Not medical advice. See a dermatologist for medical concerns.
        </Text>
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
  condition: {
    fontFamily: theme.fontFamily.display,
    fontSize: 30,
    letterSpacing: -0.5,
    color: colors.textPrimary,
    marginTop: 8,
  },
  readout: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 0.8,
    color: colors.textSecondary,
    marginTop: 6,
    textTransform: "uppercase",
  },
  meterGap: {
    marginTop: theme.spacing.md,
  },
  stripGap: {
    marginTop: theme.spacing.sm,
  },
  serious: {
    flexDirection: "row",
    gap: 10,
    alignItems: "flex-start",
    marginTop: theme.spacing.md,
    padding: theme.spacing.sm,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.oxblood,
    borderRadius: theme.borderRadius.md,
  },
  seriousText: {
    flex: 1,
    fontFamily: theme.fontFamily.bodyMedium,
    fontSize: theme.fontSize.sm,
    color: colors.oxblood,
    lineHeight: 20,
  },
  title: {
    fontFamily: theme.fontFamily.display,
    fontSize: theme.fontSize.lg,
    color: colors.textPrimary,
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
  },
  sectionHead: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "baseline",
    marginBottom: theme.spacing.sm,
  },
  sectionName: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 12,
    letterSpacing: 1,
    textTransform: "uppercase",
    color: colors.textPrimary,
  },
  sectionCount: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    color: colors.textTertiary,
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
    gap: 8,
  },
  recName: {
    flex: 1,
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.sm,
    color: colors.textPrimary,
  },
  recScore: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    color: colors.dispensary,
  },
  recFacts: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 10,
    letterSpacing: 0.4,
    color: colors.textSecondary,
    marginTop: 3,
  },
  recIngredients: {
    fontFamily: theme.fontFamily.body,
    fontSize: 12,
    color: colors.textTertiary,
    marginTop: 3,
  },
  slmItem: {
    paddingVertical: theme.spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.line,
  },
  slmName: {
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.sm,
    color: colors.textPrimary,
  },
  slmCategory: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 10,
    letterSpacing: 0.8,
    color: colors.textTertiary,
    textTransform: "uppercase",
    marginTop: 2,
  },
  slmReason: {
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
    marginTop: 4,
    lineHeight: 20,
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
    fontFamily: theme.fontFamily.body,
    fontSize: 12,
    color: colors.textSecondary,
    lineHeight: 18,
  },
});
