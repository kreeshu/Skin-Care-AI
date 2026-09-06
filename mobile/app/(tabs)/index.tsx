import React, { useState } from "react";
import { View, Text, StyleSheet, ScrollView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Button } from "../../components/ui/Button";
import { Ticket, Well, Perforation, Eyebrow } from "../../components/ui/Card";
import { ErrorState } from "../../components/ui/ErrorState";
import { RoutineStrip } from "../../components/RoutineStrip";
import { ImagePickerComponent } from "../../components/ImagePicker";
import { api } from "../../services/api";
import { toUserMessage } from "../../services/apiError";
import { useSettings } from "../../hooks/useSettings";
import { AnalysisResult } from "../../types";

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
      router.push({ pathname: `/analysis/${result.id}`, params: { result: JSON.stringify(result) } });
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
          <Eyebrow>Scan · Skincare dispensary</Eyebrow>
          <Text style={styles.title}>Check your skin,{"\n"}get tomorrow's routine.</Text>
          <Text style={styles.subtitle}>
            One clear photo in daylight. We file the reading and write the routine.
          </Text>
        </View>

        <Ticket style={styles.ticket}>
          <Eyebrow>Your photo</Eyebrow>
          <View style={styles.wellGap}>
            <Well style={styles.photoWell}>
              <ImagePickerComponent
                imageUri={imageUri}
                onImageSelected={(uri) => setImageUri(uri || null)}
              />
              <View style={styles.wellHint}>
                <Ionicons name="sunny-outline" size={14} color={colors.textSecondary} />
                <Text style={styles.wellHintText}>Daylight · no filter · face fills the frame</Text>
              </View>
            </Well>
          </View>

          <Button
            title={analyzing ? "Reading…" : "Analyze skin"}
            onPress={handleAnalyze}
            loading={analyzing}
            disabled={!imageUri || analyzing}
            size="lg"
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

          <Perforation />

          <Eyebrow>Tomorrow's shape</Eyebrow>
          <View style={styles.stripGap}>
            <RoutineStrip
              am={["Gel cleanser", "Niacinamide", "SPF 30"]}
              pm={["Gentle cleanse", "Moisturizer"]}
            />
          </View>
        </Ticket>

        <View style={styles.ledger}>
          <Eyebrow>How the reading works</Eyebrow>
          {[
            ["File", "Take or upload one photo"],
            ["Read", "We check condition and skin type"],
            ["Write", "You get an AM/PM routine that fits"],
          ].map(([k, v]) => (
            <View key={k} style={styles.ledgerRow}>
              <Text style={styles.ledgerKey}>{k}</Text>
              <Text style={styles.ledgerValue}>{v}</Text>
            </View>
          ))}
        </View>

        <View style={styles.ledger}>
          <Eyebrow>Checks 7 common conditions</Eyebrow>
          <Text style={styles.conditionLine}>
            Acne · Dark spot · Eczema · Keratosis · Milia · Rosacea · Carcinoma flagged for a
            dermatologist
          </Text>
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
    paddingTop: theme.spacing.sm,
    gap: 8,
  },
  title: {
    fontFamily: theme.fontFamily.display,
    fontSize: 30,
    lineHeight: 34,
    letterSpacing: theme.letterSpacing.tightDisplay,
    color: colors.textPrimary,
  },
  subtitle: {
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  ticket: {
    padding: theme.spacing.md,
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
    gap: 6,
    marginTop: theme.spacing.sm,
  },
  wellHintText: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 10,
    letterSpacing: 0.6,
    textTransform: "uppercase",
    color: colors.textSecondary,
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
    gap: 12,
    alignItems: "baseline",
    borderTopWidth: 1,
    borderTopColor: colors.line,
    paddingTop: 10,
  },
  ledgerKey: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 0.8,
    color: colors.dispensary,
    width: 52,
    textTransform: "uppercase",
  },
  ledgerValue: {
    flex: 1,
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.sm,
    color: colors.textPrimary,
    lineHeight: 20,
  },
  conditionLine: {
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: 22,
  },
});
