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

/** Ledger row: thumb + ruled facts, not a pastel pill card. */
export function ProductCard({ product, onPress, onFavorite, isFavorite = false }: ProductCardProps) {
  const priceInfo = formatDiscount(product.price, product.discounted_price);

  return (
    <TouchableOpacity style={styles.row} onPress={onPress} activeOpacity={0.75}>
      {product.image_url ? (
        <Image source={{ uri: product.image_url }} style={styles.thumb} resizeMode="cover" />
      ) : (
        <View style={styles.thumbPlaceholder}>
          <Ionicons name="leaf-outline" size={24} color={colors.textTertiary} />
        </View>
      )}

      <View style={styles.content}>
        <Text style={styles.index} numberOfLines={1}>
          {(product.brand || "Unknown").toUpperCase()} · {(product.source || "").toUpperCase()}
        </Text>
        <Text style={styles.name} numberOfLines={2}>
          {product.name}
        </Text>

        <Text style={styles.facts} numberOfLines={1}>
          {priceInfo.discounted || priceInfo.original} · ★ {formatRating(product.rating)} (
          {product.review_count}){product.skin_types?.[0] ? ` · ${product.skin_types[0]}` : ""}
        </Text>

        {product.category.length > 0 && (
          <View style={styles.tagRow}>
            {product.category.slice(0, 2).map((cat) => (
              <Badge key={cat} label={cat} size="sm" />
            ))}
            {priceInfo.percentage && (
              <Text style={styles.off}>{priceInfo.percentage}</Text>
            )}
          </View>
        )}
      </View>

      {onFavorite && (
        <TouchableOpacity
          onPress={onFavorite}
          hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          style={styles.fav}
        >
          <Ionicons
            name={isFavorite ? "bookmark" : "bookmark-outline"}
            size={20}
            color={isFavorite ? colors.dispensary : colors.textTertiary}
          />
        </TouchableOpacity>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    backgroundColor: colors.surface,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: colors.line,
    overflow: "hidden",
    marginBottom: theme.spacing.sm,
    minHeight: 104,
  },
  thumb: {
    width: 92,
    height: "100%",
    minHeight: 104,
    backgroundColor: colors.sage,
  },
  thumbPlaceholder: {
    width: 92,
    minHeight: 104,
    backgroundColor: colors.sage,
    justifyContent: "center",
    alignItems: "center",
  },
  content: {
    flex: 1,
    padding: theme.spacing.sm,
    gap: 3,
  },
  index: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 10,
    letterSpacing: 0.8,
    color: colors.textTertiary,
  },
  name: {
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.sm,
    color: colors.textPrimary,
    lineHeight: 19,
  },
  facts: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    color: colors.textSecondary,
  },
  tagRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    marginTop: 4,
    alignItems: "center",
  },
  off: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 10,
    color: colors.dispensary,
    letterSpacing: 0.4,
  },
  fav: {
    padding: theme.spacing.sm,
    alignSelf: "flex-start",
  },
});

export { formatPrice };
