import React from "react";
import { View, Text, Image, TouchableOpacity, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../constants/colors";
import { theme } from "../constants/theme";
import { formatPrice, formatDiscount, formatRating } from "../utils/format";
import { Product } from "../types";
import { Badge } from "./ui/Badge";

interface ProductCardProps {
  product: Product;
  onPress: () => void;
  onFavorite?: () => void;
  isFavorite?: boolean;
}

export function ProductCard({
  product,
  onPress,
  onFavorite,
  isFavorite = false,
}: ProductCardProps) {
  const priceInfo = formatDiscount(product.price, product.discounted_price);

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
      {product.image_url ? (
        <Image
          source={{ uri: product.image_url }}
          style={styles.image}
          resizeMode="cover"
        />
      ) : (
        <View style={styles.imagePlaceholder}>
          <Ionicons name="image-outline" size={32} color={colors.textTertiary} />
        </View>
      )}

      <View style={styles.content}>
        <Text style={styles.brand} numberOfLines={1}>
          {product.brand}
        </Text>
        <Text style={styles.name} numberOfLines={2}>
          {product.name}
        </Text>

        <View style={styles.priceRow}>
          <Text style={styles.price}>{priceInfo.discounted || priceInfo.original}</Text>
          {priceInfo.discounted && (
            <Text style={styles.originalPrice}>{priceInfo.original}</Text>
          )}
          {priceInfo.percentage && (
            <Badge
              label={priceInfo.percentage}
              color={colors.white}
              backgroundColor={colors.success}
              size="sm"
            />
          )}
        </View>

        <View style={styles.metaRow}>
          <View style={styles.rating}>
            <Ionicons name="star" size={14} color="#FFC107" />
            <Text style={styles.ratingText}>{formatRating(product.rating)}</Text>
            <Text style={styles.reviewCount}>({product.review_count})</Text>
          </View>

          {onFavorite && (
            <TouchableOpacity onPress={onFavorite} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
              <Ionicons
                name={isFavorite ? "heart" : "heart-outline"}
                size={20}
                color={isFavorite ? colors.error : colors.textTertiary}
              />
            </TouchableOpacity>
          )}
        </View>

        {product.category.length > 0 && (
          <View style={styles.categoryRow}>
            {product.category.slice(0, 3).map((cat) => (
              <Badge
                key={cat}
                label={cat}
                color={colors.primaryDark}
                backgroundColor={colors.primaryLight}
                size="sm"
              />
            ))}
          </View>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    backgroundColor: colors.surface,
    borderRadius: theme.borderRadius.md,
    overflow: "hidden",
    marginBottom: theme.spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  image: {
    width: 100,
    height: 120,
    backgroundColor: colors.surfaceVariant,
  },
  imagePlaceholder: {
    width: 100,
    height: 120,
    backgroundColor: colors.surfaceVariant,
    justifyContent: "center",
    alignItems: "center",
  },
  content: {
    flex: 1,
    padding: theme.spacing.sm,
    justifyContent: "space-between",
  },
  brand: {
    fontSize: theme.fontSize.xs,
    color: colors.textTertiary,
    fontWeight: theme.fontWeight.medium,
    textTransform: "uppercase",
  },
  name: {
    fontSize: theme.fontSize.sm,
    fontWeight: theme.fontWeight.semibold,
    color: colors.textPrimary,
    marginTop: 2,
  },
  priceRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginTop: 4,
  },
  price: {
    fontSize: theme.fontSize.md,
    fontWeight: theme.fontWeight.bold,
    color: colors.primaryDark,
  },
  originalPrice: {
    fontSize: theme.fontSize.xs,
    color: colors.textTertiary,
    textDecorationLine: "line-through",
  },
  metaRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 4,
  },
  rating: {
    flexDirection: "row",
    alignItems: "center",
    gap: 2,
  },
  ratingText: {
    fontSize: theme.fontSize.xs,
    fontWeight: theme.fontWeight.semibold,
    color: colors.textPrimary,
  },
  reviewCount: {
    fontSize: theme.fontSize.xs,
    color: colors.textTertiary,
  },
  categoryRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 4,
    marginTop: 6,
  },
});
