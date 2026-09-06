import React, { useState } from "react";
import { View, StyleSheet, ScrollView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Button } from "../../components/ui/Button";
import { Card, Well } from "../../components/ui/Card";
import { DisplayHeading, Body, BodySm, Caption } from "../../components/ui/Typography";
import { ErrorState } from "../../components/ui/ErrorState";
import { RoutineStrip } from "../../components/RoutineStrip";
import { ImagePickerComponent } from "../../components/ImagePicker";
import { api } from "../../services/api";
import { toUserMessage } from "../../services/apiError";
import { useSettings } from "../../hooks/useSettings";
import { AnalysisResult } from "../../types";

const HOW_IT_WORKS: Array<[string, string]> = [
  ["Take", "One clear photo in daylight"],
  ["Check", "Condition and skin type from the photo"],
  ["Follow", "Morning and evening steps that fit"],
];

const CONDITION_LINE = "Acne · Dark spot · Eczema · Keratosis · Milia · Rosacea · Carcinoma is flagged for a dermatologist";

export default function ScanScreen() {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState<unknown>(null);
  const router = useRouter();
  const { settings } = useSettings();

  const handleAnalyze = async () => {
    if (!imageUri) return;

    setAnalyzing(true);
    setAnalyzeError(null);
    try {
      const result = (await api.analyzeImage(imageUri, settings.useSlm)) as AnalysisResult;
      router.push({
        pathname: "/analysis/[id]",
        params: { id: result.id, result: JSON.stringify(result) },
      });
    } catch (error: any) {
      console.error("Analysis failed:", error);
      setAnalyzeError(error);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.header}>
          <DisplayHeading>Check your skin.</DisplayHeading>
          <BodySm>One clear photo in daylight — get a routine that fits what we see.</BodySm>
        </View>

        <Card variant="elevated">
          <Body style={styles.sectionTitle}>Your photo</Body>
          <View style={styles.wellGap}>
            <Well style={styles.photoWell}>
              <ImagePickerComponent
                imageUri={imageUri}
                onImageSelected={(uri) => setImageUri(uri || null)}
              />
              <View style={styles.wellHint}>
                <Ionicons name="sunny-outline" size={14} color={colors.textSecondary} />
                <Caption>Daylight · no filter · face fills the frame</Caption>
              </View>
            </Well>
          </View>

          <Button
            title={analyzing ? "Checking…" : "Check my skin"}
            onPress={handleAnalyze}
            loading={analyzing}
            disabled={!imageUri || analyzing}
            size="lg"
            fullWidth
            style={styles.analyzeButton}
          />
          {analyzeError ? (
            <ErrorState
              compact
              title={toUserMessage(analyzeError).title}
              message={toUserMessage(analyzeError).message}
              baseUrl={api.getBaseUrl()}
              onRetry={handleAnalyze}
              retryLabel="Try again"
            />
          ) : null}

          <Body style={styles.sectionTitle}>A sample routine</Body>
          <View style={styles.stripGap}>
            <RoutineStrip
              am={["Gel cleanser", "Niacinamide", "SPF 30"]}
              pm={["Gentle cleanse", "Moisturizer"]}
            />
          </View>
        </Card>

        <View style={styles.ledger}>
          <Body style={styles.sectionTitle}>How it works</Body>
          {HOW_IT_WORKS.map(([k, v]) => (
            <View key={k} style={styles.ledgerRow}>
              <Caption style={styles.ledgerKey}>{k}</Caption>
              <BodySm style={styles.ledgerValue}>{v}</BodySm>
            </View>
          ))}
        </View>

        <View style={styles.ledger}>
          <Body style={styles.sectionTitle}>Covers 7 common conditions</Body>
          <BodySm style={styles.conditionLine}>{CONDITION_LINE}</BodySm>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: theme.spacing.md,
    paddingBottom: theme.spacing.xxl,
    gap: theme.spacing.md,
  },
  header: {
    paddingTop: theme.spacing.md,
    gap: theme.spacing.xs2,
  },
  sectionTitle: {
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.md,
  },
  wellGap: {
    marginTop: theme.spacing.sm,
  },
  photoWell: {
    padding: theme.spacing.sm,
  },
  wellHint: {
    flexDirection: "row",
    alignItems: "center",
    gap: theme.spacing.xs2,
    marginTop: theme.spacing.sm,
  },
  analyzeButton: {
    marginTop: theme.spacing.md,
  },
  stripGap: {
    marginTop: theme.spacing.sm,
  },
  ledger: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    gap: 10,
  },
  ledgerRow: {
    flexDirection: "row",
    gap: theme.spacing.md - 4,
    alignItems: "baseline",
    borderTopWidth: 1,
    borderTopColor: colors.line,
    paddingTop: 10,
  },
  ledgerKey: {
    color: colors.dispensary,
    width: 52,
  },
  ledgerValue: {
    flex: 1,
    lineHeight: 20,
  },
  conditionLine: {
    lineHeight: 22,
  },
});
