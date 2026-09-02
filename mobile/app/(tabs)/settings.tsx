import React from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Switch,
  TouchableOpacity,
  Alert,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Card } from "../../components/ui/Card";
import { useSettings } from "../../hooks/useSettings";
import { useHistory } from "../../hooks/useHistory";

export default function SettingsScreen() {
  const { settings, update } = useSettings();
  const { clearAll } = useHistory();

  const handleClearHistory = () => {
    Alert.alert("Clear History", "Are you sure you want to clear all scan history?", [
      { text: "Cancel", style: "cancel" },
      { text: "Clear", style: "destructive", onPress: clearAll },
    ]);
  };

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.header}>
          <Text style={styles.title}>Settings</Text>
        </View>

        <Card variant="elevated" style={styles.section}>
          <Text style={styles.sectionTitle}>Preferences</Text>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>AI Explanations</Text>
              <Text style={styles.settingDescription}>
                Enable on-device SLM for product explanations and routines
              </Text>
            </View>
            <Switch
              value={settings.useSlm}
              onValueChange={(val) => update({ useSlm: val })}
              trackColor={{ false: colors.border, true: colors.primaryLight }}
              thumbColor={settings.useSlm ? colors.accent : colors.textTertiary}
            />
          </View>

          <View style={styles.divider} />

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Skin Type Preference</Text>
              <Text style={styles.settingDescription}>
                {settings.skinTypePreference
                  ? `Currently: ${settings.skinTypePreference}`
                  : "Auto-detected from image"}
              </Text>
            </View>
          </View>

          <View style={styles.skinTypeOptions}>
            {[null, "dry", "normal", "oily"].map((type) => (
              <TouchableOpacity
                key={type || "auto"}
                style={[
                  styles.skinTypeChip,
                  settings.skinTypePreference === type && styles.skinTypeChipActive,
                ]}
                onPress={() => update({ skinTypePreference: type })}
              >
                <Text
                  style={[
                    styles.skinTypeText,
                    settings.skinTypePreference === type && styles.skinTypeTextActive,
                  ]}
                >
                  {type ? type.charAt(0).toUpperCase() + type.slice(1) : "Auto"}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </Card>

        <Card variant="elevated" style={styles.section}>
          <Text style={styles.sectionTitle}>Data</Text>

          <TouchableOpacity style={styles.settingRow} onPress={handleClearHistory}>
            <View style={styles.settingInfo}>
              <Text style={[styles.settingLabel, { color: colors.error }]}>
                Clear Scan History
              </Text>
              <Text style={styles.settingDescription}>
                Remove all saved scan results
              </Text>
            </View>
            <Ionicons name="chevron-forward" size={18} color={colors.textTertiary} />
          </TouchableOpacity>
        </Card>

        <Card variant="elevated" style={styles.section}>
          <Text style={styles.sectionTitle}>About</Text>

          <View style={styles.aboutRow}>
            <Text style={styles.aboutLabel}>Model</Text>
            <Text style={styles.aboutValue}>EfficientNetB0 Multi-task</Text>
          </View>
          <View style={styles.aboutRow}>
            <Text style={styles.aboutLabel}>Conditions</Text>
            <Text style={styles.aboutValue}>7 skin conditions</Text>
          </View>
          <View style={styles.aboutRow}>
            <Text style={styles.aboutLabel}>Skin Types</Text>
            <Text style={styles.aboutValue}>Dry, Normal, Oily</Text>
          </View>
          <View style={styles.aboutRow}>
            <Text style={styles.aboutLabel}>Products</Text>
            <Text style={styles.aboutValue}>1,500+ from Nepal</Text>
          </View>
          <View style={styles.aboutRow}>
            <Text style={styles.aboutLabel}>Sources</Text>
            <Text style={styles.aboutValue}>ForEveryNG, Jeevee, Oriflame</Text>
          </View>
        </Card>

        <View style={styles.disclaimer}>
          <Ionicons name="information-circle-outline" size={16} color={colors.textTertiary} />
          <Text style={styles.disclaimerText}>
            These are cosmetic recommendations only and do not constitute medical advice.
            Please consult a dermatologist for medical concerns.
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
  },
  header: {
    paddingTop: theme.spacing.sm,
    paddingBottom: theme.spacing.md,
  },
  title: {
    fontSize: theme.fontSize.xl,
    fontWeight: theme.fontWeight.bold,
    color: colors.primaryDark,
  },
  section: {
    marginBottom: theme.spacing.md,
  },
  sectionTitle: {
    fontSize: theme.fontSize.md,
    fontWeight: theme.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: theme.spacing.md,
  },
  settingRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: theme.spacing.sm,
  },
  settingInfo: {
    flex: 1,
    marginRight: theme.spacing.sm,
  },
  settingLabel: {
    fontSize: theme.fontSize.md,
    fontWeight: theme.fontWeight.medium,
    color: colors.textPrimary,
  },
  settingDescription: {
    fontSize: theme.fontSize.xs,
    color: colors.textTertiary,
    marginTop: 2,
  },
  divider: {
    height: 1,
    backgroundColor: colors.border,
    marginVertical: theme.spacing.xs,
  },
  skinTypeOptions: {
    flexDirection: "row",
    gap: 8,
    marginTop: theme.spacing.sm,
  },
  skinTypeChip: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: theme.borderRadius.sm,
    backgroundColor: colors.surfaceVariant,
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.border,
  },
  skinTypeChipActive: {
    backgroundColor: colors.primaryLight,
    borderColor: colors.primary,
  },
  skinTypeText: {
    fontSize: theme.fontSize.xs,
    fontWeight: theme.fontWeight.medium,
    color: colors.textSecondary,
  },
  skinTypeTextActive: {
    color: colors.primaryDark,
  },
  aboutRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 6,
  },
  aboutLabel: {
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
  },
  aboutValue: {
    fontSize: theme.fontSize.sm,
    fontWeight: theme.fontWeight.medium,
    color: colors.textPrimary,
  },
  disclaimer: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
    marginTop: theme.spacing.sm,
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
