import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
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
import { Eyebrow } from "../../components/ui/Card";
import { ProductCard } from "../../components/ProductCard";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { ErrorState } from "../../components/ui/ErrorState";
import { api } from "../../services/api";
import { toUserMessage } from "../../services/apiError";
import { useFavorites } from "../../hooks/useFavorites";
import { Product, ProductsResponse } from "../../types";

const SORT_OPTIONS = [
  { label: "Top rated", value: "rating" },
  { label: "Price ↑", value: "price_low" },
  { label: "Price ↓", value: "price_high" },
  { label: "Reviewed", value: "reviews" },
];

export default function CatalogScreen() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState("rating");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [categories, setCategories] = useState<string[]>([]);
  const [error, setError] = useState<unknown>(null);
  const [retryKey, setRetryKey] = useState(0);
  const router = useRouter();
  const { favorites, toggle } = useFavorites();

  useEffect(() => {
    api
      .getCategories()
      .then((data) => setCategories(data.categories))
      .catch((err) => {
        console.warn("Failed to load categories:", err);
      });
  }, [retryKey]);

  const loadProducts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = (await api.getProducts({
        search: search || undefined,
        category: selectedCategory || undefined,
        sort_by: sortBy,
        page,
        page_size: 20,
      })) as ProductsResponse;
      setProducts(data.products);
      setTotalPages(data.total_pages);
      setTotal(data.total);
    } catch (err) {
      console.error("Failed to load products:", err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [search, selectedCategory, sortBy, page, retryKey]);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  const handleSearch = (text: string) => {
    setSearch(text);
    setPage(1);
  };

  const handleCategorySelect = (category: string | null) => {
    setSelectedCategory(category === selectedCategory ? null : category);
    setPage(1);
  };

  const handleRetry = () => {
    setRetryKey((k) => k + 1);
  };

  if (!loading && error) {
    const { title, message } = toUserMessage(error);
    return (
      <SafeAreaView style={styles.container} edges={["top"]}>
        <View style={styles.header}>
          <Eyebrow>Index</Eyebrow>
          <Text style={styles.title}>Find what fits your routine.</Text>
        </View>
        <ErrorState
          title={title}
          message={message}
          baseUrl={api.getBaseUrl()}
          onRetry={handleRetry}
        />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      <View style={styles.header}>
        <Eyebrow>
          Index · {loading ? "…" : `${total} items`}
        </Eyebrow>
        <Text style={styles.title}>Find what fits your routine.</Text>
      </View>

      <View style={styles.searchRow}>
        <Ionicons name="search-outline" size={18} color={colors.textTertiary} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search cleanser, niacinamide, SPF…"
          placeholderTextColor={colors.textTertiary}
          value={search}
          onChangeText={handleSearch}
        />
        {search.length > 0 && (
          <TouchableOpacity onPress={() => handleSearch("")}>
            <Ionicons name="close-circle" size={18} color={colors.textTertiary} />
          </TouchableOpacity>
        )}
      </View>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.tabs}
      >
        <TouchableOpacity
          style={[styles.tab, selectedCategory === null && styles.tabActive]}
          onPress={() => handleCategorySelect(selectedCategory)}
        >
          <Text style={[styles.tabText, selectedCategory === null && styles.tabTextActive]}>
            All
          </Text>
        </TouchableOpacity>
        {categories.map((cat) => (
          <TouchableOpacity
            key={cat}
            style={[styles.tab, selectedCategory === cat && styles.tabActive]}
            onPress={() => handleCategorySelect(cat)}
          >
            <Text style={[styles.tabText, selectedCategory === cat && styles.tabTextActive]}>
              {cat}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <View style={styles.sortRow}>
        <Text style={styles.sortLabel}>Sort</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {SORT_OPTIONS.map((option) => (
            <TouchableOpacity
              key={option.value}
              style={[styles.sortItem, sortBy === option.value && styles.sortItemActive]}
              onPress={() => {
                setSortBy(option.value);
                setPage(1);
              }}
            >
              <Text
                style={[styles.sortText, sortBy === option.value && styles.sortTextActive]}
              >
                {option.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {loading ? (
        <LoadingSpinner />
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
            <View style={styles.empty}>
              <Eyebrow>Nothing filed</Eyebrow>
              <Text style={styles.emptyTitle}>No matches for this combination.</Text>
              <Text style={styles.emptyText}>Loosen one filter — start with category.</Text>
            </View>
          }
        />
      )}

      {totalPages > 1 && !loading && !error && (
        <View style={styles.pagination}>
          <TouchableOpacity
            style={[styles.pageButton, page <= 1 && styles.pageButtonDisabled]}
            onPress={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
          >
            <Ionicons name="chevron-back" size={18} color={page <= 1 ? colors.textTertiary : colors.pine} />
          </TouchableOpacity>
          <Text style={styles.pageText}>
            {page} / {totalPages}
          </Text>
          <TouchableOpacity
            style={[styles.pageButton, page >= totalPages && styles.pageButtonDisabled]}
            onPress={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
          >
            <Ionicons name="chevron-forward" size={18} color={page >= totalPages ? colors.textTertiary : colors.pine} />
          </TouchableOpacity>
        </View>
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
    paddingHorizontal: theme.spacing.md,
    paddingTop: theme.spacing.sm,
    gap: 6,
  },
  title: {
    fontFamily: theme.fontFamily.display,
    fontSize: theme.fontSize.xl,
    letterSpacing: -0.3,
    color: colors.textPrimary,
  },
  searchRow: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    paddingHorizontal: theme.spacing.sm,
    height: 46,
    gap: 8,
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
    gap: 0,
  },
  tab: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginRight: 4,
    borderBottomWidth: 2,
    borderBottomColor: "transparent",
  },
  tabActive: {
    borderBottomColor: colors.dispensary,
  },
  tabText: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 0.8,
    textTransform: "uppercase",
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
    gap: 12,
  },
  sortLabel: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 0.8,
    textTransform: "uppercase",
    color: colors.textTertiary,
  },
  sortItem: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    marginRight: 8,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 6,
    backgroundColor: colors.surface,
  },
  sortItemActive: {
    backgroundColor: colors.pine,
    borderColor: colors.pine,
  },
  sortText: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
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
  empty: {
    alignItems: "flex-start",
    gap: 6,
    paddingVertical: 48,
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
    fontFamily: theme.fontFamily.mono,
    fontSize: 12,
    color: colors.textPrimary,
  },
});
