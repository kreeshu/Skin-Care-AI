import React from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { ConditionBadge } from "../../components/ConditionBadge";
import { Button } from "../../components/ui/Button";
import { useHistory } from "../../hooks/useHistory";
import { formatDate } from "../../utils/format";
import { ScanHistoryItem } from "../../types";

export default function HistoryScreen() {
  const { history, loading, removeScan, clearAll } = useHistory();
  const router = useRouter();

  const handleClearAll = () => {
    Alert.alert("Clear History", "Are you sure you want to clear all scan history?", [
      { text: "Cancel", style: "cancel" },
      { text: "Clear", style: "destructive", onPress: clearAll },
    ]);
  };

  const handleDelete = (id: string) => {
    Alert.alert("Delete Scan", "Remove this scan from history?", [
      { text: "Cancel", style: "cancel" },
      { text: "Delete", style: "destructive", onPress: () => removeScan(id) },
    ]);
  };

  const renderItem = ({ item }: { item: ScanHistoryItem }) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() => router.push({ pathname: `/analysis/${item.id}`, params: { result: JSON.stringify(item.result) } })}
      activeOpacity={0.7}
    >
      <View style={styles.cardHeader}>
        <ConditionBadge condition={item.condition} size="sm" />
        <TouchableOpacity onPress={() => handleDelete(item.id)} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
          <Ionicons name="trash-outline" size={18} color={colors.textTertiary} />
        </TouchableOpacity>
      </View>
      <View style={styles.cardBody}>
        <View style={styles.infoRow}>
          <Ionicons name="water-outline" size={14} color={colors.textTertiary} />
          <Text style={styles.infoText}>Skin type: {item.skin_type}</Text>
        </View>
        <View style={styles.infoRow}>
          <Ionicons name="time-outline" size={14} color={colors.textTertiary} />
          <Text style={styles.infoText}>{formatDate(item.date)}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Scan History</Text>
          <Text style={styles.subtitle}>{history.length} scans</Text>
        </View>
        {history.length > 0 && (
          <Button title="Clear All" variant="ghost" size="sm" onPress={handleClearAll} />
        )}
      </View>

      {history.length === 0 ? (
        <View style={styles.empty}>
          <Ionicons name="time-outline" size={64} color={colors.textTertiary} />
          <Text style={styles.emptyTitle}>No scan history</Text>
          <Text style={styles.emptyText}>
            Your skin analysis results will appear here
          </Text>
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
    alignItems: "center",
    paddingHorizontal: theme.spacing.md,
    paddingTop: theme.spacing.sm,
    paddingBottom: theme.spacing.sm,
  },
  title: {
    fontSize: theme.fontSize.xl,
    fontWeight: theme.fontWeight.bold,
    color: colors.primaryDark,
  },
  subtitle: {
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
    marginTop: 2,
  },
  listContent: {
    padding: theme.spacing.md,
    paddingBottom: 100,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: theme.spacing.sm,
  },
  cardBody: {
    gap: 4,
  },
  infoRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  infoText: {
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
  },
  empty: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: theme.spacing.xxl,
  },
  emptyTitle: {
    fontSize: theme.fontSize.lg,
    fontWeight: theme.fontWeight.bold,
    color: colors.textPrimary,
    marginTop: theme.spacing.md,
  },
  emptyText: {
    fontSize: theme.fontSize.sm,
    color: colors.textTertiary,
    marginTop: theme.spacing.xs,
    textAlign: "center",
  },
});
