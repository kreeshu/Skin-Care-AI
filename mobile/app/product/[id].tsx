import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
} from "react-native";
import { useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Badge } from "../../components/ui/Badge";
import { Eyebrow } from "../../components/ui/Card";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { ErrorState } from "../../components/ui/ErrorState";
import { Product } from "../../types";
import { api } from "../../services/api";
import { isApiError, toUserMessage } from "../../services/apiError";
import { useFavorites } from "../../hooks/useFavorites";
import { formatDiscount, formatRating } from "../../utils/format";

export default function ProductDetailScreen() {
  const params = useLocalSearchParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);
  const [retryKey, setRetryKey] = useState(0);
  const { favorites, toggle } = useFavorites();

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = (await api.getProduct(Number(params.id))) as Product;
        if (!cancelled) setProduct(data);
      } catch (err) {
        console.error("Failed to load product:", err);
        if (!cancelled) setError(err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [params.id, retryKey]);

  if (loading) return <LoadingSpinner />;
  if (error) {
    if (isApiError(error) && error.kind === "http" && error.status === 404) {
      return (
        <View style={styles.empty}>
          <Eyebrow>Label missing</Eyebrow>
          <Text style={styles.emptyTitle}>This item is not on file.</Text>
        </View>
      );
    }
    const { title, message } = toUserMessage(error);
    return (
      <ErrorState
        title={title}
        message={message}
        baseUrl={api.getBaseUrl()}
        onRetry={() => setRetryKey((k) => k + 1)}
      />
    );
  }
  if (!product) {
    return (
      <View style={styles.empty}>
        <Eyebrow>Label missing</Eyebrow>
        <Text style={styles.emptyTitle}>This item is not on file.</Text>
      </View>
    );
  }

  const priceInfo = formatDiscount(product.price, product.discounted_price);
  const isFav = favorites.includes(product.product_id);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      {product.image_url ? (
        <Image source={{ uri: product.image_url }} style={styles.image} resizeMode="cover" />
      ) : (
        <View style={styles.imagePlaceholder}>
          <Ionicons name="leaf-outline" size={40} color={colors.textTertiary} />
        </View>
      )}

      <Eyebrow>
        Label · {(product.brand || "Unknown").toUpperCase()} · {(product.source || "").toUpperCase()}
      </Eyebrow>
      <Text style={styles.name}>{product.name}</Text>

      <View style={styles.factTable}>
        <View style={styles.factRow}>
          <Text style={styles.factKey}>Price</Text>
          <Text style={styles.factValue}>
            {priceInfo.discounted || priceInfo.original}
            {priceInfo.discounted ? `  (was ${priceInfo.original})` : ""}
          </Text>
        </View>
        <View style={styles.factRow}>
          <Text style={styles.factKey}>Rating</Text>
          <Text style={styles.factValue}>
            ★ {formatRating(product.rating)} · {product.review_count} reviews
          </Text>
        </View>
        <View style={styles.factRow}>
          <Text style={styles.factKey}>Stock</Text>
          <Text style={[styles.factValue, product.availability !== "in_stock" && styles.oos]}>
            {product.availability === "in_stock" ? "In stock" : "Out of stock"}
          </Text>
        </View>
        <View style={[styles.factRow, styles.factLast]}>
          <Text style={styles.factKey}>Filed under</Text>
          <Text style={styles.factValue}>{product.category.slice(0, 3).join(" · ") || "—"}</Text>
        </View>
      </View>

      <TouchableOpacity
        style={[styles.fileButton, isFav && styles.fileButtonActive]}
        onPress={() => toggle(product.product_id)}
        activeOpacity={0.8}
      >
        <Ionicons
          name={isFav ? "bookmark" : "bookmark-outline"}
          size={18}
          color={isFav ? colors.white : colors.dispensary}
        />
        <Text style={[styles.fileText, isFav && styles.fileTextActive]}>
          {isFav ? "Filed in your shelf" : "File on your shelf"}
        </Text>
      </TouchableOpacity>

      {product.skin_types.length > 0 && (
        <View style={styles.tagSection}>
          <Eyebrow>Suits</Eyebrow>
          <View style={styles.tagRow}>
            {product.skin_types.map((type) => (
              <Badge key={type} label={type} size="sm" />
            ))}
          </View>
        </View>
      )}

      {product.skin_concerns.length > 0 && (
        <View style={styles.tagSection}>
          <Eyebrow>Helps with</Eyebrow>
          <View style={styles.tagRow}>
            {product.skin_concerns.map((concern) => (
              <Badge key={concern} label={concern} size="sm" />
            ))}
          </View>
        </View>
      )}

      {product.ingredients.length > 0 && (
        <View style={styles.tagSection}>
          <Eyebrow>Inside · {product.ingredients.length}</Eyebrow>
          <Text style={styles.ingredients}>{product.ingredients.join(", ")}</Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: theme.spacing.md,
    paddingBottom: theme.spacing.xxl,
    gap: 10,
  },
  image: {
    width: "100%",
    height: 280,
    backgroundColor: colors.sage,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: colors.line,
  },
  imagePlaceholder: {
    width: "100%",
    height: 180,
    backgroundColor: colors.sage,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: colors.line,
    justifyContent: "center",
    alignItems: "center",
  },
  name: {
    fontFamily: theme.fontFamily.display,
    fontSize: 26,
    letterSpacing: -0.4,
    color: colors.textPrimary,
    lineHeight: 30,
  },
  factTable: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    paddingHorizontal: theme.spacing.md,
    marginTop: 6,
  },
  factRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 12,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
  },
  factLast: {
    borderBottomWidth: 0,
  },
  factKey: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 0.8,
    textTransform: "uppercase",
    color: colors.textTertiary,
  },
  factValue: {
    flex: 1,
    textAlign: "right",
    fontFamily: theme.fontFamily.bodyMedium,
    fontSize: theme.fontSize.sm,
    color: colors.textPrimary,
  },
  oos: {
    color: colors.oxblood,
  },
  fileButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.dispensary,
    borderRadius: theme.borderRadius.md,
    paddingVertical: 13,
  },
  fileButtonActive: {
    backgroundColor: colors.pine,
    borderColor: colors.pine,
  },
  fileText: {
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.md,
    color: colors.dispensary,
  },
  fileTextActive: {
    color: colors.white,
  },
  tagSection: {
    gap: 8,
    marginTop: 6,
  },
  tagRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
  },
  ingredients: {
    fontFamily: theme.fontFamily.body,
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: 22,
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
});
