import React from "react";
import { View, Text, StyleSheet, ScrollView, Switch, TouchableOpacity, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Eyebrow } from "../../components/ui/Card";
import { useSettings } from "../../hooks/useSettings";
import { useHistory } from "../../hooks/useHistory";

export default function SettingsScreen() {
  const { settings, update } = useSettings();
  const { clearAll } = useHistory();

  const handleClearHistory = () => {
    Alert.alert("Clear filed readings?", "This removes all saved readings from this device.", [
      { text: "Keep", style: "cancel" },
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
          <Eyebrow>Setup</Eyebrow>
          <Text style={styles.title}>Set up the dispensary.</Text>
        </View>

        <View style={styles.section}>
          <Eyebrow>Reading</Eyebrow>
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Dispenser notes</Text>
              <Text style={styles.settingDescription}>
                Short explanations with each routine
              </Text>
            </View>
            <Switch
              value={settings.useSlm}
              onValueChange={(val) => update({ useSlm: val })}
              trackColor={{ false: colors.line, true: colors.sage }}
              thumbColor={settings.useSlm ? colors.dispensary : colors.textTertiary}
            />
          </View>

          <View style={styles.divider} />

          <Text style={styles.settingLabel}>Skin type on file</Text>
          <Text style={styles.settingDescription}>
            {settings.skinTypePreference ? `Filed as ${settings.skinTypePreference}` : "Read from each photo"}
          </Text>

          <View style={styles.skinTypeOptions}>
            {[null, "dry", "normal", "oily"].map((type) => (
              <TouchableOpacity
                key={type || "auto"}
                style={[
                  styles.skinTypeChoice,
                  settings.skinTypePreference === type && styles.skinTypeChoiceActive,
                ]}
                onPress={() => update({ skinTypePreference: type })}
              >
                <Text
                  style={[
                    styles.skinTypeText,
                    settings.skinTypePreference === type && styles.skinTypeTextActive,
                  ]}
                >
                  {type ? type.toUpperCase() : "AUTO"}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.section}>
          <Eyebrow>Filed readings</Eyebrow>
          <TouchableOpacity style={styles.settingRow} onPress={handleClearHistory}>
            <View style={styles.settingInfo}>
              <Text style={[styles.settingLabel, { color: colors.oxblood }]}>
                Clear filed readings
              </Text>
              <Text style={styles.settingDescription}>Removes saved results on this device</Text>
            </View>
            <Ionicons name="chevron-forward" size={18} color={colors.textTertiary} />
          </TouchableOpacity>
        </View>

        <View style={styles.section}>
          <Eyebrow>On file</Eyebrow>
          {[
            ["Reader", "EfficientNetB0, multi-task"],
            ["Conditions", "7 entries"],
            ["Skin types", "Dry · Normal · Oily"],
            ["Stock", "1,500+ items from Nepal"],
            ["Shelves", "Jeevee · Oriflame"],
          ].map(([k, v]) => (
            <View key={k} style={styles.aboutRow}>
              <Text style={styles.aboutLabel}>{k}</Text>
              <Text style={styles.aboutValue}>{v}</Text>
            </View>
          ))}
        </View>

        <View style={styles.footnote}>
          <Ionicons name="reader-outline" size={16} color={colors.textSecondary} />
          <Text style={styles.footnoteText}>
            Cosmetic guidance only. See a dermatologist for medical concerns.
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
    gap: 6,
  },
  title: {
    fontFamily: theme.fontFamily.display,
    fontSize: theme.fontSize.xl,
    letterSpacing: -0.3,
    color: colors.textPrimary,
  },
  section: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    gap: 10,
  },
  settingRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 4,
  },
  settingInfo: {
    flex: 1,
    marginRight: theme.spacing.sm,
    gap: 2,
  },
  settingLabel: {
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.md,
    color: colors.textPrimary,
  },
  settingDescription: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 0.3,
    color: colors.textSecondary,
  },
  divider: {
    height: 1,
    backgroundColor: colors.line,
  },
  skinTypeOptions: {
    flexDirection: "row",
    gap: 8,
    marginTop: 4,
  },
  skinTypeChoice: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 6,
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
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 0.8,
    color: colors.textSecondary,
  },
  skinTypeTextActive: {
    color: colors.white,
  },
  aboutRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 12,
    paddingVertical: 7,
    borderTopWidth: 1,
    borderTopColor: colors.line,
  },
  aboutLabel: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 0.6,
    textTransform: "uppercase",
    color: colors.textTertiary,
  },
  aboutValue: {
    fontFamily: theme.fontFamily.bodyMedium,
    fontSize: theme.fontSize.sm,
    color: colors.textPrimary,
    textAlign: "right",
  },
  footnote: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
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
