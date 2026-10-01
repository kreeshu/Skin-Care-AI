import React, { useState } from "react";
import { View, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Eyebrow, DisplayLg, Body, BodySm } from "../../components/ui/Typography";
import { useSettings } from "../../hooks/useSettings";
import { api } from "../../services/api";

const SKIN_TYPE_CHOICES: { value: string | null; label: string }[] = [
  { value: null, label: "Not provided" },
  { value: "dry", label: "Dry" },
  { value: "normal", label: "Normal" },
  { value: "oily", label: "Oily" },
  { value: "combination", label: "Combination" },
  { value: "sensitive", label: "Sensitive" },
];

const ABOUT_ROWS: [string, string][] = [
  ["Model", "EfficientNetB0, multi-label"],
  ["Concerns", "5 cosmetic observations"],
  ["Skin type", "Provided by you"],
  ["Stock", "1,500+ items from Nepal"],
  ["Shops", "Jeevee · Oriflame"],
];

export default function SettingsScreen() {
  const { settings, update } = useSettings();
  const [connStatus, setConnStatus] = useState<string | null>(null);
  const [connBusy, setConnBusy] = useState(false);

  const testConnection = async () => {
    setConnBusy(true);
    setConnStatus(null);
    try {
      await api.healthCheck();
      setConnStatus("Reachable");
    } catch (e: any) {
      setConnStatus(e?.message ?? "Unreachable");
    } finally {
      setConnBusy(false);
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
          <DisplayLg>Settings.</DisplayLg>
        </View>

        <View style={styles.section}>
          <Body style={styles.sectionTitle}>Skin type</Body>
          <BodySm>
            {settings.skinTypePreference ? `Saved as ${settings.skinTypePreference}` : "Not provided · never guessed from photos"}
          </BodySm>

          <View style={styles.skinTypeOptions}>
            {SKIN_TYPE_CHOICES.map(({ value, label }) => {
              const active = settings.skinTypePreference === value;
              return (
                <TouchableOpacity
                  key={value || "auto"}
                  style={[styles.skinTypeChoice, active && styles.skinTypeChoiceActive]}
                  onPress={() => update({ skinTypePreference: value })}
                  accessibilityRole="button"
                  accessibilityState={{ selected: active }}
                >
                  <Body style={[styles.skinTypeText, active && styles.skinTypeTextActive]}>
                    {label}
                  </Body>
                </TouchableOpacity>
              );
            })}
          </View>
        </View>

        <View style={styles.section}>
          <Body style={styles.sectionTitle}>Connection</Body>
          <BodySm numberOfLines={1}>Server · {api.getBaseUrl()}</BodySm>
          <TouchableOpacity
            style={styles.settingRow}
            onPress={testConnection}
            disabled={connBusy}
            accessibilityRole="button"
          >
            <View style={styles.settingInfo}>
              <Body>Test connection</Body>
              <BodySm>{connBusy ? "Checking…" : (connStatus ?? "Health · /api/health")}</BodySm>
            </View>
            {connBusy ? (
              <ActivityIndicator size="small" color={colors.dispensary} />
            ) : (
              <Ionicons name="chevron-forward" size={18} color={colors.textTertiary} />
            )}
          </TouchableOpacity>
        </View>

        <View style={styles.section}>
          <Body style={styles.sectionTitle}>About</Body>
          {ABOUT_ROWS.map(([k, v]) => (
            <View key={k} style={styles.aboutRow}>
              <Eyebrow style={styles.aboutLabel}>{k}</Eyebrow>
              <BodySm style={styles.aboutValue}>{v}</BodySm>
            </View>
          ))}
        </View>

        <View style={styles.footnote}>
          <Ionicons name="information-circle-outline" size={16} color={colors.textSecondary} />
          <BodySm style={styles.footnoteText}>
            Cosmetic guidance only. See a dermatologist for medical concerns.
          </BodySm>
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
    gap: theme.spacing.xs2,
  },
  section: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    gap: 10,
  },
  sectionTitle: {
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.md,
    color: colors.textPrimary,
  },
  settingRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: theme.spacing.xs,
  },
  settingInfo: {
    flex: 1,
    marginRight: theme.spacing.sm,
    gap: 2,
  },
  skinTypeOptions: {
    flexDirection: "row",
    gap: theme.spacing.sm,
    marginTop: theme.spacing.xs,
  },
  skinTypeChoice: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 999,
    backgroundColor: colors.paper,
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.line,
  },
  skinTypeChoiceActive: {
    backgroundColor: colors.pine,
    borderColor: colors.pine,
  },
  skinTypeText: {
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
  },
  skinTypeTextActive: {
    color: colors.white,
  },
  aboutRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: theme.spacing.md,
    paddingVertical: 7,
    borderTopWidth: 1,
    borderTopColor: colors.line,
  },
  aboutLabel: {
    color: colors.textTertiary,
  },
  aboutValue: {
    color: colors.textPrimary,
    textAlign: "right",
  },
  footnote: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: theme.spacing.sm,
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
