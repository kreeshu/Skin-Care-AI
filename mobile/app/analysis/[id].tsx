import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { colors, conditionColors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Card, CardHeader } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { ConfidenceBar } from "../../components/ui/ConfidenceBar";
import { Button } from "../../components/ui/Button";
import { RoutineStep } from "../../components/RoutineStep";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { AnalysisResult, ProductRecommendation } from "../../types";
import { useFavorites } from "../../hooks/useFavorites";

function ProductRecCard({
  rec,
  onPress,
}: {
  rec: ProductRecommendation;
  onPress: () => void;
}) {
  return (
    <TouchableOpacity style={styles.recCard} onPress={onPress} activeOpacity={0.7}>
      <View style={styles.recHeader}>
        <Text style={styles.recName} numberOfLines={1}>
          {rec.name}
        </Text>
        <Text style={styles.recScore}>{rec.score.toFixed(3)}</Text>
      </View>
      <Text style={styles.recBrand}>
        {rec.brand} | Rs. {Math.round(rec.discounted_price || rec.price || 0).toLocaleString()} |{" "}
        {rec.rating ? `${rec.rating.toFixed(1)} stars` : "No rating"}
      </Text>
      {rec.matching_ingredients.length > 0 && (
        <Text style={styles.recIngredients} numberOfLines={1}>
          {rec.matching_ingredients.join(", ")}
        </Text>
      )}
    </TouchableOpacity>
  );
}

export default function AnalysisScreen() {
  const params = useLocalSearchParams<{ id: string; result?: string }>();
  const router = useRouter();
  const { favorites, toggle } = useFavorites();
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

  const conditionColor = conditionColors[result.detected_condition] || colors.textTertiary;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <View
        style={[
          styles.conditionCard,
          { backgroundColor: `${conditionColor}10`, borderColor: `${conditionColor}30` },
        ]}
      >
        <View style={[styles.conditionDot, { backgroundColor: conditionColor }]} />
        <View style={styles.conditionInfo}>
          <Text style={[styles.conditionName, { color: conditionColor }]}>
            {result.detected_condition}
          </Text>
          <Text style={styles.conditionConfidence}>
            {Math.round(result.condition_confidence * 100)}% confidence
          </Text>
        </View>
      </View>

      <Text style={styles.title}>{result.title}</Text>
      <Text style={styles.description}>{result.description}</Text>

      {result.skin_type && (
        <View style={styles.skinTypeRow}>
          <Ionicons name="water-outline" size={16} color={colors.primary} />
          <Text style={styles.skinTypeText}>
            Skin type: <Text style={styles.skinTypeValue}>{result.skin_type}</Text>
            {result.skin_type_confidence > 0 && (
              <Text> ({Math.round(result.skin_type_confidence * 100)}%)</Text>
            )}
          </Text>
        </View>
      )}

      {result.is_medical && result.detected_condition === "Carcinoma" && (
        <View style={styles.warningCard}>
          <Ionicons name="warning" size={20} color={colors.error} />
          <Text style={styles.warningText}>
            This may indicate a serious skin condition. Please consult a dermatologist
            immediately.
          </Text>
        </View>
      )}

      {result.recommendations && Object.keys(result.recommendations).length > 0 && (
        <>
          <Text style={styles.sectionTitle}>Recommended Products</Text>
          {Object.entries(result.recommendations).map(([category, recs]) => (
            <Card key={category} variant="outlined" style={styles.categoryCard}>
              <CardHeader
                title={category.toUpperCase()}
                subtitle={`${recs.length} products`}
              />
              {recs.slice(0, 3).map((rec) => (
                <ProductRecCard
                  key={rec.product_id}
                  rec={rec}
                  onPress={() => router.push(`/product/${rec.product_id}`)}
                />
              ))}
            </Card>
          ))}
        </>
      )}

      {result.slm && (
        <>
          <Text style={styles.sectionTitle}>AI Explanations</Text>
          <Card variant="elevated">
            {result.slm.chosen.map((item, idx) => (
              <View key={idx} style={styles.slmItem}>
                <Text style={styles.slmName}>{item.name}</Text>
                <Text style={styles.slmCategory}>{item.category}</Text>
                <Text style={styles.slmReason}>{item.reason}</Text>
              </View>
            ))}
          </Card>

          {(result.slm.routine.am.length > 0 || result.slm.routine.pm.length > 0) && (
            <Card variant="elevated" style={styles.routineCard}>
              <Text style={styles.routineTitle}>Your Routine</Text>
              <View style={styles.routineGrid}>
                {result.slm.routine.am.length > 0 && (
                  <View style={styles.routineColumn}>
                    <Text style={styles.routineLabel}>AM</Text>
                    {result.slm.routine.am.map((step, idx) => (
                      <Text key={idx} style={styles.routineStep}>
                        {idx + 1}. {step}
                      </Text>
                    ))}
                  </View>
                )}
                {result.slm.routine.pm.length > 0 && (
                  <View style={styles.routineColumn}>
                    <Text style={styles.routineLabel}>PM</Text>
                    {result.slm.routine.pm.map((step, idx) => (
                      <Text key={idx} style={styles.routineStep}>
                        {idx + 1}. {step}
                      </Text>
                    ))}
                  </View>
                )}
              </View>
            </Card>
          )}
        </>
      )}

      {result.routine_suggestion.length > 0 && (
        <>
          <Text style={styles.sectionTitle}>Suggested Routine</Text>
          <Card variant="elevated">
            {result.routine_suggestion.map((step, idx) => (
              <RoutineStep key={idx} step={idx + 1} title={step} />
            ))}
          </Card>
        </>
      )}

      <View style={styles.disclaimer}>
        <Ionicons name="information-circle-outline" size={16} color={colors.textTertiary} />
        <Text style={styles.disclaimerText}>
          These are cosmetic recommendations only and do not constitute medical advice.
          Please consult a dermatologist for medical concerns.
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
  },
  conditionCard: {
    flexDirection: "row",
    alignItems: "center",
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    marginBottom: theme.spacing.md,
  },
  conditionDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: theme.spacing.sm,
  },
  conditionInfo: {
    flex: 1,
  },
  conditionName: {
    fontSize: theme.fontSize.xl,
    fontWeight: theme.fontWeight.bold,
  },
  conditionConfidence: {
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
    marginTop: 2,
  },
  title: {
    fontSize: theme.fontSize.lg,
    fontWeight: theme.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: 4,
  },
  description: {
    fontSize: theme.fontSize.md,
    color: colors.textSecondary,
    lineHeight: 22,
    marginBottom: theme.spacing.md,
  },
  skinTypeRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: theme.spacing.md,
  },
  skinTypeText: {
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
  },
  skinTypeValue: {
    fontWeight: theme.fontWeight.bold,
    color: colors.primaryDark,
  },
  warningCard: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 12,
    padding: theme.spacing.md,
    backgroundColor: `${colors.error}10`,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: `${colors.error}30`,
    marginBottom: theme.spacing.md,
  },
  warningText: {
    flex: 1,
    fontSize: theme.fontSize.sm,
    color: colors.error,
    lineHeight: 20,
  },
  sectionTitle: {
    fontSize: theme.fontSize.lg,
    fontWeight: theme.fontWeight.bold,
    color: colors.textPrimary,
    marginTop: theme.spacing.md,
    marginBottom: theme.spacing.sm,
  },
  categoryCard: {
    marginBottom: theme.spacing.sm,
  },
  recCard: {
    paddingVertical: theme.spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  recHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  recName: {
    flex: 1,
    fontSize: theme.fontSize.sm,
    fontWeight: theme.fontWeight.semibold,
    color: colors.textPrimary,
    marginRight: 8,
  },
  recScore: {
    fontSize: theme.fontSize.xs,
    fontWeight: theme.fontWeight.bold,
    color: colors.primary,
  },
  recBrand: {
    fontSize: theme.fontSize.xs,
    color: colors.textSecondary,
    marginTop: 2,
  },
  recIngredients: {
    fontSize: theme.fontSize.xs,
    color: colors.textTertiary,
    marginTop: 4,
  },
  slmItem: {
    marginBottom: theme.spacing.sm,
    paddingBottom: theme.spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  slmName: {
    fontSize: theme.fontSize.sm,
    fontWeight: theme.fontWeight.bold,
    color: colors.textPrimary,
  },
  slmCategory: {
    fontSize: theme.fontSize.xs,
    color: colors.textTertiary,
    textTransform: "uppercase",
  },
  slmReason: {
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
    marginTop: 4,
    lineHeight: 18,
  },
  routineCard: {
    marginTop: theme.spacing.sm,
  },
  routineTitle: {
    fontSize: theme.fontSize.md,
    fontWeight: theme.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: theme.spacing.sm,
  },
  routineGrid: {
    flexDirection: "row",
    gap: theme.spacing.md,
  },
  routineColumn: {
    flex: 1,
  },
  routineLabel: {
    fontSize: theme.fontSize.sm,
    fontWeight: theme.fontWeight.bold,
    color: colors.primaryDark,
    marginBottom: 4,
  },
  routineStep: {
    fontSize: theme.fontSize.xs,
    color: colors.textSecondary,
    marginBottom: 4,
    lineHeight: 18,
  },
  disclaimer: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
    marginTop: theme.spacing.lg,
    padding: theme.spacing.md,
    backgroundColor: colors.surfaceVariant,
    borderRadius: theme.borderRadius.md,
  },
  disclaimerText: {
    flex: 1,
    fontSize: theme.fontSize.xs,
    color: colors.textTertiary,
    lineHeight: 18,
  },
});
