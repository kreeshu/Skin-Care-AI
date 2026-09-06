import React from "react";
import {
  View,
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
import { Eyebrow, DisplayLg, BodySm, Caption } from "../../components/ui/Typography";
import { ErrorState } from "../../components/ui/ErrorState";
import { EmptyState } from "../../components/ui/EmptyState";
import { LoadingState } from "../../components/ui/LoadingState";
import { Product } from "../../types";
import { api } from "../../services/api";
import { isApiError, toUserMessage } from "../../services/apiError";
import { useFetcher } from "../../hooks/useFetcher";
import { useFavorites } from "../../hooks/useFavorites";
import { formatDiscount, formatRating } from "../../utils/format";

function parseProductId(raw: string | undefined): number | null {
  if (!raw) return null;
  const n = Number(raw);
  return Number.isFinite(n) && n > 0 ? n : null;
}

export default function ProductDetailScreen() {
  const params = useLocalSearchParams<{ id: string }>();
  const productId = parseProductId(params.id);
  const { favorites, toggle } = useFavorites();

  const { data: product, loading, error, retry } = useFetcher<Product>(
    () => api.getProduct(productId as number),
    [params.id],
    { enabled: productId !== null },
  );

  if (productId === null) {
    return (
      <View style={styles.container}>
        <EmptyState
          eyebrow="Not found"
          title="Unknown product."
          message="The link is malformed. Try opening it again from the shop."
          icon="search-outline"
        />
      </View>
    );
  }

  if (loading) return <LoadingState eyebrow="Product · loading" rows={2} compact />;

  if (error) {
    if (isApiError(error) && error.kind === "http" && error.status === 404) {
      return (
        <View style={styles.container}>
          <EmptyState
            eyebrow="Not found"
            title="This item is not available."
            message="It may have been delisted, or the id changed."
            icon="search-outline"
            actionLabel="Back to shop"
          />
        </View>
      );
    }
    const { title, message } = toUserMessage(error);
    return (
      <View style={styles.container}>
        <ErrorState title={title} message={message} baseUrl={api.getBaseUrl()} onRetry={retry} />
      </View>
    );
  }

  if (!product) {
    return (
      <View style={styles.container}>
        <EmptyState eyebrow="Not found" title="This item is not available." icon="search-outline" />
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
          <Ionicons name="image-outline" size={40} color={colors.dispensary} />
        </View>
      )}

      <Eyebrow>
        {(product.brand || "Unknown").toUpperCase()} · {(product.source || "").toUpperCase()}
      </Eyebrow>
      <DisplayLg>{product.name}</DisplayLg>

      <View style={styles.factTable}>
        <View style={styles.factRow}>
          <Caption style={styles.factKey}>Price</Caption>
          <BodySm style={styles.factValue}>
            {priceInfo.discounted || priceInfo.original}
            {priceInfo.discounted ? `  (was ${priceInfo.original})` : ""}
          </BodySm>
        </View>
        <View style={styles.factRow}>
          <Caption style={styles.factKey}>Rating</Caption>
          <BodySm style={styles.factValue}>
            ★ {formatRating(product.rating)} · {product.review_count} reviews
          </BodySm>
        </View>
        <View style={styles.factRow}>
          <Caption style={styles.factKey}>Availability</Caption>
          <BodySm
            style={[styles.factValue, product.availability !== "in_stock" && styles.oos]}
          >
            {product.availability === "in_stock" ? "In stock" : "Out of stock"}
          </BodySm>
        </View>
        <View style={[styles.factRow, styles.factLast]}>
          <Caption style={styles.factKey}>Category</Caption>
          <BodySm style={styles.factValue}>
            {product.category.slice(0, 3).join(" · ") || "—"}
          </BodySm>
        </View>
      </View>

      <TouchableOpacity
        style={[styles.fileButton, isFav && styles.fileButtonActive]}
        onPress={() => toggle(product.product_id)}
        activeOpacity={0.8}
        accessibilityRole="button"
        accessibilityState={{ selected: isFav }}
      >
        <Ionicons
          name={isFav ? "bookmark" : "bookmark-outline"}
          size={18}
          color={isFav ? colors.white : colors.dispensary}
        />
        <BodySm style={[styles.fileText, isFav && styles.fileTextActive]}>
          {isFav ? "Saved to your shelf" : "Save to your shelf"}
        </BodySm>
      </TouchableOpacity>

      {product.skin_types.length > 0 ? (
        <View style={styles.tagSection}>
          <Eyebrow>Suits your skin</Eyebrow>
          <View style={styles.tagRow}>
            {product.skin_types.map((type) => (
              <Badge key={type} label={type} size="sm" />
            ))}
          </View>
        </View>
      ) : null}

      {product.skin_concerns.length > 0 ? (
        <View style={styles.tagSection}>
          <Eyebrow>Helps with</Eyebrow>
          <View style={styles.tagRow}>
            {product.skin_concerns.map((concern) => (
              <Badge key={concern} label={concern} size="sm" />
            ))}
          </View>
        </View>
      ) : null}

      {product.ingredients.length > 0 ? (
        <View style={styles.tagSection}>
          <Eyebrow>Inside · {product.ingredients.length} ingredients</Eyebrow>
          <BodySm style={styles.ingredients}>{product.ingredients.join(", ")}</BodySm>
        </View>
      ) : null}
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
  factTable: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    paddingHorizontal: theme.spacing.md,
    marginTop: theme.spacing.xs2,
  },
  factRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: theme.spacing.md,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
  },
  factLast: {
    borderBottomWidth: 0,
  },
  factKey: {
    color: colors.textTertiary,
  },
  factValue: {
    flex: 1,
    textAlign: "right",
    color: colors.textPrimary,
  },
  oos: {
    color: colors.oxblood,
  },
  fileButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: theme.spacing.sm,
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
    gap: theme.spacing.sm,
    marginTop: theme.spacing.xs2,
  },
  tagRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: theme.spacing.xs2,
  },
  ingredients: {
    lineHeight: 22,
  },
});
