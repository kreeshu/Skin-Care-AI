import React, { useEffect, useState } from "react";
import { View, StyleSheet, FlatList, TouchableOpacity, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Eyebrow, DisplayLg, BodySm, Body } from "../../components/ui/Typography";
import { EmptyState } from "../../components/ui/EmptyState";
import { Button } from "../../components/ui/Button";
import { ProductCard } from "../../components/ProductCard";
import { useHistory } from "../../hooks/useHistory";
import { useFavorites } from "../../hooks/useFavorites";
import { api } from "../../services/api";
import { formatDate } from "../../utils/format";
import { Product, ScanHistoryItem } from "../../types";

export default function HistoryScreen() {
  const { history, removeScan, clearAll } = useHistory();
  const router = useRouter();
  const [tab, setTab] = useState<"results" | "products">("results");
  const { favorites, toggle } = useFavorites();
  const [products, setProducts] = useState<Product[]>([]);

  // Favorites store only ids; fetch details when the Products tab is open.
  useEffect(() => {
    if (tab !== "products") return;
    let cancelled = false;
    Promise.all(favorites.map((id) => api.getProduct(id).catch(() => null))).then((rows) => {
      if (!cancelled) setProducts(rows.filter(Boolean) as Product[]);
    });
    return () => {
      cancelled = true;
    };
  }, [tab, favorites]);

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
        <BodySm>{item.summary}</BodySm>
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
          <Eyebrow>
            Saved · {tab === "results" ? `${history.length} results` : `${favorites.length} products`}
          </Eyebrow>
          <DisplayLg>{tab === "results" ? "Your past checks." : "Your shelf."}</DisplayLg>
        </View>
        {tab === "results" && history.length > 0 ? (
          <Button title="Clear" variant="ghost" size="sm" onPress={confirmClear} />
        ) : null}
      </View>

      <View style={styles.segment}>
        {(["results", "products"] as const).map((key) => (
          <TouchableOpacity
            key={key}
            style={[styles.segmentItem, tab === key && styles.segmentActive]}
            onPress={() => setTab(key)}
            accessibilityRole="button"
            accessibilityState={{ selected: tab === key }}
          >
            <Body style={[styles.segmentText, tab === key && styles.segmentTextActive]}>
              {key === "results" ? "Results" : "Products"}
            </Body>
          </TouchableOpacity>
        ))}
      </View>

      {tab === "products" ? (
        favorites.length === 0 ? (
          <EmptyState
            eyebrow="Nothing saved yet"
            title="Saved products will land here."
            message="Tap the bookmark on any product in Shop."
            icon="bookmark-outline"
            actionLabel="Go to Shop"
            onAction={() => router.push("/(tabs)/catalog")}
          />
        ) : (
          <FlatList
            data={products}
            keyExtractor={(item) => item.product_id}
            renderItem={({ item }) => (
              <ProductCard
                product={item}
                onPress={() => router.push(`/product/${item.product_id}`)}
                onFavorite={() => toggle(item.product_id)}
                isFavorite
              />
            )}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
          />
        )
      ) : history.length === 0 ? (
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
  segment: {
    flexDirection: "row",
    gap: theme.spacing.sm,
    paddingHorizontal: theme.spacing.md,
    paddingTop: theme.spacing.md,
  },
  segmentItem: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 999,
    backgroundColor: colors.paper,
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.line,
  },
  segmentActive: {
    backgroundColor: colors.pine,
    borderColor: colors.pine,
  },
  segmentText: {
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
  },
  segmentTextActive: {
    color: colors.white,
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
