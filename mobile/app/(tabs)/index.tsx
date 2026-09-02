import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { ImagePickerComponent } from "../../components/ImagePicker";
import { api } from "../../services/api";
import { useSettings } from "../../hooks/useSettings";
import { useFavorites } from "../../hooks/useFavorites";
import { AnalysisResult } from "../../types";

export default function ScanScreen() {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const router = useRouter();
  const { settings } = useSettings();
  const { favorites, toggle } = useFavorites();

  const handleAnalyze = async () => {
    if (!imageUri) return;

    setAnalyzing(true);
    try {
      const result = (await api.analyzeImage(imageUri, settings.useSlm)) as AnalysisResult;
      router.push({ pathname: `/analysis/${result.id}`, params: { result: JSON.stringify(result) } });
    } catch (error: any) {
      Alert.alert("Analysis Failed", error.message || "Could not analyze the image. Please try again.");
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
          <Text style={styles.title}>SkinCare AI</Text>
          <Text style={styles.subtitle}>
            AI-powered skin condition detection{"\n"}with product recommendations
          </Text>
        </View>

        <Card variant="elevated" style={styles.inputCard}>
          <Text style={styles.sectionTitle}>Input Image</Text>
          <ImagePickerComponent imageUri={imageUri} onImageSelected={setImageUri} />

          <Button
            title={analyzing ? "Analyzing..." : "Analyze Skin"}
            onPress={handleAnalyze}
            loading={analyzing}
            disabled={!imageUri || analyzing}
            size="lg"
            style={styles.analyzeButton}
          />
        </Card>

        <Card variant="outlined" style={styles.infoCard}>
          <Text style={styles.infoTitle}>How it works</Text>
          <View style={styles.steps}>
            <View style={styles.step}>
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>1</Text>
              </View>
              <Text style={styles.stepText}>Upload a skin image or take a photo</Text>
            </View>
            <View style={styles.step}>
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>2</Text>
              </View>
              <Text style={styles.stepText}>AI detects condition and skin type</Text>
            </View>
            <View style={styles.step}>
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>3</Text>
              </View>
              <Text style={styles.stepText}>Get personalized product recommendations</Text>
            </View>
          </View>
        </Card>

        <Card variant="outlined" style={styles.infoCard}>
          <Text style={styles.infoTitle}>Detects 7 conditions</Text>
          <View style={styles.conditionList}>
            {["Acne", "Carcinoma", "Dark Spot", "Eczema", "Keratosis", "Milia", "Rosacea"].map(
              (condition) => (
                <Text key={condition} style={styles.conditionItem}>
                  {condition}
                </Text>
              )
            )}
          </View>
        </Card>
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
  },
  header: {
    marginBottom: theme.spacing.lg,
    paddingTop: theme.spacing.sm,
  },
  title: {
    fontSize: theme.fontSize.xxl,
    fontWeight: theme.fontWeight.bold,
    color: colors.primaryDark,
  },
  subtitle: {
    fontSize: theme.fontSize.md,
    color: colors.textSecondary,
    marginTop: 4,
    lineHeight: 22,
  },
  inputCard: {
    marginBottom: theme.spacing.md,
  },
  sectionTitle: {
    fontSize: theme.fontSize.lg,
    fontWeight: theme.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: theme.spacing.md,
  },
  analyzeButton: {
    marginTop: theme.spacing.md,
  },
  infoCard: {
    marginBottom: theme.spacing.md,
  },
  infoTitle: {
    fontSize: theme.fontSize.md,
    fontWeight: theme.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: theme.spacing.md,
  },
  steps: {
    gap: theme.spacing.sm,
  },
  step: {
    flexDirection: "row",
    alignItems: "center",
    gap: theme.spacing.sm,
  },
  stepNumber: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.primaryLight,
    justifyContent: "center",
    alignItems: "center",
  },
  stepNumberText: {
    fontSize: theme.fontSize.sm,
    fontWeight: theme.fontWeight.bold,
    color: colors.primaryDark,
  },
  stepText: {
    flex: 1,
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
  },
  conditionList: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  conditionItem: {
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
    backgroundColor: colors.surfaceVariant,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 100,
    overflow: "hidden",
  },
});
