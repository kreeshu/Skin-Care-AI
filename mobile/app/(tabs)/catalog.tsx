import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  ScrollView,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Eyebrow, DisplayLg } from "../../components/ui/Typography";
import { ProductCard } from "../../components/ProductCard";
import { LoadingState } from "../../components/ui/LoadingState";
import { ErrorState } from "../../components/ui/ErrorState";
import { EmptyState } from "../../components/ui/EmptyState";
import { api } from "../../services/api";
import { toUserMessage } from "../../services/apiError";
import { useFetcher } from "../../hooks/useFetcher";
import { useFavorites } from "../../hooks/useFavorites";
import { Product, ProductsResponse } from "../../types";

const SORT_OPTIONS = [
  { label: "Top rated", value: "rating" },
  { label: "Price ↑", value: "price_low" },
  { label: "Price ↓", value: "price_high" },
  { label: "Reviewed", value: "reviews" },
];

const PAGE_SIZE = 20;

export default function CatalogScreen() {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState("rating");
  const [page, setPage] = useState(1);
  const [categories, setCategories] = useState<string[]>([]);
  const router = useRouter();
  const { favorites, toggle } = useFavorites();

  // Categories are non-critical — load silently, don't block the list.
  useEffect(() => {
    api
      .getCategories()
      .then((data) => setCategories(data.categories))
      .catch((err) => console.warn("Failed to load categories:", err));
  }, []);

  const { data, loading, error, retry } = useFetcher<ProductsResponse>(
    () =>
      api.getProducts({
        search: search || undefined,
        category: selectedCategory || undefined,
        sort_by: sortBy,
        page,
        page_size: PAGE_SIZE,
      }),
    [search, selectedCategory, sortBy, page],
  );

  const products = data?.products ?? [];
  const totalPages = data?.total_pages ?? 1;
  const total = data?.total ?? 0;

  const handleSearch = (text: string) => {
    setSearch(text);
    setPage(1);
  };

  const handleCategorySelect = (category: string | null) => {
    setSelectedCategory(category === selectedCategory ? null : category);
    setPage(1);
  };

  // Show the error state as a full screen when the *first* load fails.
  if (!loading && error && products.length === 0) {
    const { title, message } = toUserMessage(error);
    return (
      <SafeAreaView style={styles.container} edges={["top"]}>
        <Header total={0} />
        <ErrorState
          title={title}
          message={message}
          baseUrl={api.getBaseUrl()}
          onRetry={retry}
        />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      <Header total={total} loading={loading} />

      <View style={styles.searchRow}>
        <Ionicons name="search-outline" size={18} color={colors.textTertiary} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search cleanser, niacinamide, SPF…"
          placeholderTextColor={colors.textTertiary}
          value={search}
          onChangeText={handleSearch}
        />
        {search.length > 0 ? (
          <TouchableOpacity onPress={() => handleSearch("")} accessibilityRole="button">
            <Ionicons name="close-circle" size={18} color={colors.textTertiary} />
          </TouchableOpacity>
        ) : null}
      </View>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.tabs}
      >
        <TouchableOpacity
          style={[styles.tab, selectedCategory === null && styles.tabActive]}
          onPress={() => handleCategorySelect(null)}
        >
          <Eyebrow style={[styles.tabText, selectedCategory === null && styles.tabTextActive]}>
            All
          </Eyebrow>
        </TouchableOpacity>
        {categories.map((cat) => (
          <TouchableOpacity
            key={cat}
            style={[styles.tab, selectedCategory === cat && styles.tabActive]}
            onPress={() => handleCategorySelect(cat)}
          >
            <Eyebrow style={[styles.tabText, selectedCategory === cat && styles.tabTextActive]}>
              {cat}
            </Eyebrow>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <View style={styles.sortRow}>
        <Eyebrow style={styles.sortLabel}>Sort</Eyebrow>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {SORT_OPTIONS.map((option) => {
            const active = sortBy === option.value;
            return (
              <TouchableOpacity
                key={option.value}
                style={[styles.sortItem, active && styles.sortItemActive]}
                onPress={() => {
                  setSortBy(option.value);
                  setPage(1);
                }}
                accessibilityRole="button"
                accessibilityState={{ selected: active }}
              >
                <Eyebrow style={[styles.sortText, active && styles.sortTextActive]}>
                  {option.label}
                </Eyebrow>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </View>

      {loading && products.length === 0 ? (
        <LoadingState eyebrow="Shop · loading" rows={4} compact />
      ) : (
        <FlatList
          data={products}
          keyExtractor={(item) => String(item.product_id)}
          renderItem={({ item }) => (
            <ProductCard
              product={item}
              onPress={() => router.push(`/product/${item.product_id}`)}
              onFavorite={() => toggle(item.product_id)}
              isFavorite={favorites.includes(item.product_id)}
            />
          )}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={
            <EmptyState
              eyebrow="No matches"
              title="No matches for this combination."
              message="Clear one filter — start with category."
              icon="search-outline"
              actionLabel="Clear filters"
              onAction={() => {
                setSearch("");
                setSelectedCategory(null);
                setPage(1);
              }}
            />
          }
        />
      )}

      {totalPages > 1 && products.length > 0 ? (
        <View style={styles.pagination}>
          <TouchableOpacity
            style={[styles.pageButton, page <= 1 && styles.pageButtonDisabled]}
            onPress={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
            accessibilityRole="button"
          >
            <Ionicons name="chevron-back" size={18} color={page <= 1 ? colors.textTertiary : colors.pine} />
          </TouchableOpacity>
          <Eyebrow style={styles.pageText}>
            {page} / {totalPages}
          </Eyebrow>
          <TouchableOpacity
            style={[styles.pageButton, page >= totalPages && styles.pageButtonDisabled]}
            onPress={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            accessibilityRole="button"
          >
            <Ionicons name="chevron-forward" size={18} color={page >= totalPages ? colors.textTertiary : colors.pine} />
          </TouchableOpacity>
        </View>
      ) : null}
    </SafeAreaView>
  );
}

function Header({ total, loading }: { total: number; loading?: boolean }) {
  return (
    <View style={styles.header}>
      <Eyebrow>Shop{loading ? " · loading" : ` · ${total} items`}</Eyebrow>
      <DisplayLg>Find what fits your routine.</DisplayLg>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    paddingHorizontal: theme.spacing.md,
    paddingTop: theme.spacing.sm,
    gap: theme.spacing.xs2,
  },
  searchRow: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 999,
    paddingHorizontal: theme.spacing.md,
    height: 52,
    gap: theme.spacing.sm,
    margin: theme.spacing.md,
    marginBottom: theme.spacing.sm,
  },
  searchInput: {
    flex: 1,
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.md,
    color: colors.textPrimary,
  },
  tabs: {
    paddingHorizontal: theme.spacing.md,
  },
  tab: {
    paddingHorizontal: theme.spacing.md - 4,
    paddingVertical: theme.spacing.sm,
    marginRight: theme.spacing.xs,
    borderBottomWidth: 2,
    borderBottomColor: "transparent",
  },
  tabActive: {
    borderBottomColor: colors.dispensary,
  },
  tabText: {
    color: colors.textSecondary,
  },
  tabTextActive: {
    color: colors.pine,
  },
  sortRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: theme.spacing.md,
    marginVertical: theme.spacing.sm,
    gap: theme.spacing.md - 4,
  },
  sortLabel: {
    color: colors.textTertiary,
  },
  sortItem: {
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    marginRight: theme.spacing.sm,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 999,
    backgroundColor: colors.surface,
  },
  sortItemActive: {
    backgroundColor: colors.pine,
    borderColor: colors.pine,
  },
  sortText: {
    color: colors.textSecondary,
  },
  sortTextActive: {
    color: colors.white,
  },
  listContent: {
    padding: theme.spacing.md,
    paddingTop: theme.spacing.sm,
    paddingBottom: 100,
  },
  pagination: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: theme.spacing.sm,
    gap: theme.spacing.md,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.line,
  },
  pageButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.sage,
    borderWidth: 1,
    borderColor: colors.line,
    justifyContent: "center",
    alignItems: "center",
  },
  pageButtonDisabled: {
    opacity: 0.5,
  },
  pageText: {
    color: colors.textPrimary,
  },
});
