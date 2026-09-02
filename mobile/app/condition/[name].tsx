import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
} from "react-native";
import { useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { colors, conditionColors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { RoutineStep } from "../../components/RoutineStep";
import { Condition } from "../../types";
import { api } from "../../services/api";

export default function ConditionDetailScreen() {
  const params = useLocalSearchParams<{ name: string }>();
  const [condition, setCondition] = useState<Condition | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = (await api.getCondition(params.name || "")) as Condition;
        setCondition(data);
      } catch (error) {
        console.error("Failed to load condition:", error);
      } finally {
        setLoading(false);
      }
    })();
  }, [params.name]);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (!condition) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>Condition not found</Text>
      </View>
    );
  }

  const conditionColor = conditionColors[condition.name] || colors.textTertiary;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <View
        style={[
          styles.headerCard,
          { backgroundColor: `${conditionColor}10`, borderColor: `${conditionColor}30` },
        ]}
      >
        <View style={[styles.dot, { backgroundColor: conditionColor }]} />
        <View>
          <Text style={[styles.conditionName, { color: conditionColor }]}>
            {condition.title}
          </Text>
          {condition.is_medical && (
            <Badge label="Medical" color={colors.white} backgroundColor={colors.error} size="sm" />
          )}
        </View>
      </View>

      <Text style={styles.description}>{condition.description}</Text>

      {condition.causes.length > 0 && (
        <Card variant="elevated" style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="help-circle-outline" size={20} color={colors.primary} />
            <Text style={styles.sectionTitle}>Causes</Text>
          </View>
          {condition.causes.map((cause, idx) => (
            <View key={idx} style={styles.listItem}>
              <View style={[styles.bullet, { backgroundColor: conditionColor }]} />
              <Text style={styles.listText}>{cause}</Text>
            </View>
          ))}
        </Card>
      )}

      {condition.recommended_ingredients.length > 0 && (
        <Card variant="elevated" style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="flask-outline" size={20} color={colors.primary} />
            <Text style={styles.sectionTitle}>Recommended Ingredients</Text>
          </View>
          <View style={styles.tagRow}>
            {condition.recommended_ingredients.map((ing) => (
              <Badge
                key={ing}
                label={ing}
                color={colors.primaryDark}
                backgroundColor={colors.primaryLight}
              />
            ))}
          </View>
        </Card>
      )}

      {condition.recommended_categories.length > 0 && (
        <Card variant="elevated" style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="basket-outline" size={20} color={colors.primary} />
            <Text style={styles.sectionTitle}>Product Categories</Text>
          </View>
          <View style={styles.tagRow}>
            {condition.recommended_categories.map((cat) => (
              <Badge
                key={cat}
                label={cat}
                color={colors.info}
                backgroundColor={`${colors.info}15`}
              />
            ))}
          </View>
        </Card>
      )}

      {condition.avoid_ingredients.length > 0 && (
        <Card variant="elevated" style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="close-circle-outline" size={20} color={colors.error} />
            <Text style={[styles.sectionTitle, { color: colors.error }]}>
              Avoid Ingredients
            </Text>
          </View>
          <View style={styles.tagRow}>
            {condition.avoid_ingredients.map((ing) => (
              <Badge
                key={ing}
                label={ing}
                color={colors.error}
                backgroundColor={`${colors.error}15`}
              />
            ))}
          </View>
        </Card>
      )}

      {condition.tips.length > 0 && (
        <Card variant="elevated" style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="bulb-outline" size={20} color={colors.warning} />
            <Text style={styles.sectionTitle}>Tips</Text>
          </View>
          {condition.tips.map((tip, idx) => (
            <View key={idx} style={styles.listItem}>
              <View style={[styles.bullet, { backgroundColor: colors.warning }]} />
              <Text style={styles.listText}>{tip}</Text>
            </View>
          ))}
        </Card>
      )}

      {condition.routine_steps.length > 0 && (
        <Card variant="elevated" style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="calendar-outline" size={20} color={colors.primary} />
            <Text style={styles.sectionTitle}>Suggested Routine</Text>
          </View>
          {condition.routine_steps.map((step, idx) => (
            <RoutineStep key={idx} step={idx + 1} title={step} />
          ))}
        </Card>
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
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: colors.background,
  },
  headerCard: {
    flexDirection: "row",
    alignItems: "center",
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    marginBottom: theme.spacing.md,
    gap: 12,
  },
  dot: {
    width: 16,
    height: 16,
    borderRadius: 8,
  },
  conditionName: {
    fontSize: theme.fontSize.xl,
    fontWeight: theme.fontWeight.bold,
  },
  description: {
    fontSize: theme.fontSize.md,
    color: colors.textSecondary,
    lineHeight: 22,
    marginBottom: theme.spacing.md,
  },
  section: {
    marginBottom: theme.spacing.md,
  },
  sectionHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: theme.spacing.sm,
  },
  sectionTitle: {
    fontSize: theme.fontSize.md,
    fontWeight: theme.fontWeight.bold,
    color: colors.textPrimary,
  },
  listItem: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 6,
    gap: 8,
  },
  bullet: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  listText: {
    flex: 1,
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  tagRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  empty: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  emptyText: {
    fontSize: theme.fontSize.md,
    color: colors.textTertiary,
  },
});
