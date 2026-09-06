import React from "react";
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Eyebrow } from "../../components/ui/Card";
import { ConditionBadge } from "../../components/ConditionBadge";
import { Button } from "../../components/ui/Button";
import { useHistory } from "../../hooks/useHistory";
import { formatDate } from "../../utils/format";
import { ScanHistoryItem } from "../../types";

export default function HistoryScreen() {
  const { history, removeScan, clearAll } = useHistory();
  const router = useRouter();

  const confirmClear = () => {
    Alert.alert("Clear filed readings?", "This removes all saved readings from this device.", [
      { text: "Keep", style: "cancel" },
      { text: "Clear", style: "destructive", onPress: clearAll },
    ]);
  };

  const renderItem = ({ item }: { item: ScanHistoryItem }) => (
    <TouchableOpacity
      style={styles.row}
      onPress={() => router.push({ pathname: `/analysis/${item.id}`, params: { result: JSON.stringify(item.result) } })}
      activeOpacity={0.75}
    >
      <View style={styles.rowHead}>
        <ConditionBadge condition={item.condition} size="sm" />
        <Text style={styles.date}>{formatDate(item.date).toUpperCase()}</Text>
      </View>
      <Text style={styles.skinLine}>
        {item.skin_type ? item.skin_type.toUpperCase() : "SKIN TYPE —"} · FILED {item.id.slice(0, 8).toUpperCase()}
      </Text>
      <TouchableOpacity
        onPress={() => removeScan(item.id)}
        hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
        style={styles.trash}
      >
        <Ionicons name="trash-outline" size={16} color={colors.textTertiary} />
      </TouchableOpacity>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      <View style={styles.header}>
        <View style={styles.headerText}>
          <Eyebrow>Filed · {history.length} readings</Eyebrow>
          <Text style={styles.title}>Past readings.</Text>
        </View>
        {history.length > 0 && (
          <Button title="Clear" variant="ghost" size="sm" onPress={confirmClear} />
        )}
      </View>

      {history.length === 0 ? (
        <View style={styles.empty}>
          <Eyebrow>Nothing filed yet</Eyebrow>
          <Text style={styles.emptyTitle}>Your readings will land here.</Text>
          <Text style={styles.emptyText}>File your first photo from Scan.</Text>
          <Button title="Go to Scan" onPress={() => router.push("/(tabs)")} style={styles.cta} />
        </View>
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
    gap: 12,
  },
  headerText: {
    flex: 1,
    gap: 6,
  },
  title: {
    fontFamily: theme.fontFamily.display,
    fontSize: theme.fontSize.xl,
    letterSpacing: -0.3,
    color: colors.textPrimary,
  },
  listContent: {
    padding: theme.spacing.md,
    paddingBottom: 100,
    gap: 8,
  },
  row: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    gap: 6,
  },
  rowHead: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 8,
  },
  date: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 10,
    letterSpacing: 0.8,
    color: colors.textTertiary,
  },
  skinLine: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 0.4,
    color: colors.textSecondary,
  },
  trash: {
    position: "absolute",
    right: 8,
    bottom: 8,
    padding: 6,
  },
  empty: {
    flex: 1,
    justifyContent: "center",
    alignItems: "flex-start",
    padding: theme.spacing.lg,
    gap: 8,
  },
  emptyTitle: {
    fontFamily: theme.fontFamily.display,
    fontSize: theme.fontSize.lg,
    color: colors.textPrimary,
  },
  emptyText: {
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
  },
  cta: {
    marginTop: theme.spacing.sm,
  },
});
