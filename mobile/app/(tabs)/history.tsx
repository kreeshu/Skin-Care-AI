import React from "react";
import { View, StyleSheet, FlatList, TouchableOpacity, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Eyebrow, DisplayLg, BodySm } from "../../components/ui/Typography";
import { EmptyState } from "../../components/ui/EmptyState";
import { ConditionBadge } from "../../components/ConditionBadge";
import { Button } from "../../components/ui/Button";
import { useHistory } from "../../hooks/useHistory";
import { formatDate } from "../../utils/format";
import { ScanHistoryItem } from "../../types";

export default function HistoryScreen() {
  const { history, removeScan, clearAll } = useHistory();
  const router = useRouter();

  const confirmClear = () => {
    Alert.alert("Clear saved results?", "This removes all saved results from this device.", [
      { text: "Keep", style: "cancel" },
      { text: "Clear", style: "destructive", onPress: clearAll },
    ]);
  };

  const renderItem = ({ item }: { item: ScanHistoryItem }) => (
    <TouchableOpacity
      style={styles.row}
      onPress={() =>
        router.push({ pathname: "/analysis/[id]", params: { id: item.id, result: JSON.stringify(item.result) } })
      }
      activeOpacity={0.75}
      accessibilityRole="button"
    >
      <View style={styles.rowHead}>
        <ConditionBadge condition={item.condition} size="sm" />
        <BodySm style={styles.date}>{formatDate(item.date)}</BodySm>
      </View>
      <BodySm style={styles.skinLine}>
        {item.skin_type ? item.skin_type : "Skin type unknown"}
      </BodySm>
      <TouchableOpacity
        onPress={() => removeScan(item.id)}
        hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
        style={styles.trash}
        accessibilityRole="button"
        accessibilityLabel="Remove this reading"
      >
        <Ionicons name="trash-outline" size={16} color={colors.textTertiary} />
      </TouchableOpacity>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      <View style={styles.header}>
        <View style={styles.headerText}>
          <Eyebrow>Saved · {history.length} results</Eyebrow>
          <DisplayLg>Your past checks.</DisplayLg>
        </View>
        {history.length > 0 ? (
          <Button title="Clear" variant="ghost" size="sm" onPress={confirmClear} />
        ) : null}
      </View>

      {history.length === 0 ? (
        <EmptyState
          eyebrow="Nothing saved yet"
          title="Your results will land here."
          message="Send your first photo from Chat."
          icon="bookmark-outline"
          actionLabel="Go to Chat"
          onAction={() => router.push("/(tabs)")}
        />
      ) : (
        <FlatList
          data={history}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    paddingHorizontal: theme.spacing.md,
    paddingTop: theme.spacing.sm,
    gap: theme.spacing.md,
  },
  headerText: {
    flex: 1,
    gap: theme.spacing.xs2,
  },
  listContent: {
    padding: theme.spacing.md,
    paddingBottom: 100,
    gap: theme.spacing.sm,
  },
  row: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    gap: theme.spacing.xs2,
  },
  rowHead: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: theme.spacing.sm,
  },
  date: {
    color: colors.textTertiary,
  },
  skinLine: {
    color: colors.textSecondary,
  },
  trash: {
    position: "absolute",
    right: theme.spacing.sm,
    bottom: theme.spacing.sm,
    padding: theme.spacing.xs2,
  },
});
