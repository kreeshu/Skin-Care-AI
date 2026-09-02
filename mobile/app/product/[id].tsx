import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  Linking,
  ActivityIndicator,
} from "react-native";
import { useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { Product } from "../../types";
import { api } from "../../services/api";
import { useFavorites } from "../../hooks/useFavorites";
import { formatPrice, formatDiscount, formatRating } from "../../utils/format";

export default function ProductDetailScreen() {
  const params = useLocalSearchParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const { favorites, toggle } = useFavorites();

  useEffect(() => {
    (async () => {
      try {
        const data = (await api.getProduct(Number(params.id))) as Product;
        setProduct(data);
      } catch (error) {
        console.error("Failed to load product:", error);
      } finally {
        setLoading(false);
      }
    })();
  }, [params.id]);

  if (loading) return <LoadingSpinner />;
  if (!product) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>Product not found</Text>
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
        <Image
          source={{ uri: product.image_url }}
          style={styles.image}
          resizeMode="cover"
        />
      ) : (
        <View style={styles.imagePlaceholder}>
          <Ionicons name="image-outline" size={64} color={colors.textTertiary} />
        </View>
      )}

      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.brand}>{product.brand}</Text>
          <Text style={styles.name}>{product.name}</Text>
        </View>
        <TouchableOpacity
          style={styles.favoriteButton}
          onPress={() => toggle(product.product_id)}
          hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
        >
          <Ionicons
            name={isFav ? "heart" : "heart-outline"}
            size={24}
            color={isFav ? colors.error : colors.textTertiary}
          />
        </TouchableOpacity>
      </View>

      <View style={styles.priceSection}>
        <Text style={styles.price}>{priceInfo.discounted || priceInfo.original}</Text>
        {priceInfo.discounted && (
          <>
            <Text style={styles.originalPrice}>{priceInfo.original}</Text>
            <Badge
              label={priceInfo.percentage!}
              color={colors.white}
              backgroundColor={colors.success}
              size="sm"
            />
          </>
        )}
      </View>

      <View style={styles.metaRow}>
        <View style={styles.rating}>
          {[1, 2, 3, 4, 5].map((star) => (
            <Ionicons
              key={star}
              name={
                product.rating && star <= Math.round(product.rating)
                  ? "star"
                  : "star-outline"
              }
              size={16}
              color="#FFC107"
            />
          ))}
          <Text style={styles.ratingText}>{formatRating(product.rating)}</Text>
          <Text style={styles.reviewCount}>({product.review_count} reviews)</Text>
        </View>
      </View>

      <View style={styles.infoRow}>
        <View style={styles.infoItem}>
          <Ionicons name="pricetag-outline" size={16} color={colors.primary} />
          <Text style={styles.infoText}>{product.source}</Text>
        </View>
        <View style={styles.infoItem}>
          <Ionicons
            name={product.availability === "in_stock" ? "checkmark-circle-outline" : "close-circle-outline"}
            size={16}
            color={product.availability === "in_stock" ? colors.success : colors.error}
          />
          <Text style={styles.infoText}>
            {product.availability === "in_stock" ? "In Stock" : "Out of Stock"}
          </Text>
        </View>
      </View>

      {product.category.length > 0 && (
        <View style={styles.tagSection}>
          <Text style={styles.tagLabel}>Categories</Text>
          <View style={styles.tagRow}>
            {product.category.map((cat) => (
              <Badge
                key={cat}
                label={cat}
                color={colors.primaryDark}
                backgroundColor={colors.primaryLight}
              />
            ))}
          </View>
        </View>
      )}

      {product.skin_types.length > 0 && (
        <View style={styles.tagSection}>
          <Text style={styles.tagLabel}>Skin Types</Text>
          <View style={styles.tagRow}>
            {product.skin_types.map((type) => (
              <Badge
                key={type}
                label={type}
                color={colors.info}
                backgroundColor={`${colors.info}15`}
              />
            ))}
          </View>
        </View>
      )}

      {product.skin_concerns.length > 0 && (
        <View style={styles.tagSection}>
          <Text style={styles.tagLabel}>Skin Concerns</Text>
          <View style={styles.tagRow}>
            {product.skin_concerns.map((concern) => (
              <Badge
                key={concern}
                label={concern}
                color={colors.warning}
                backgroundColor={`${colors.warning}15`}
              />
            ))}
          </View>
        </View>
      )}

      {product.ingredients.length > 0 && (
        <View style={styles.tagSection}>
          <Text style={styles.tagLabel}>Ingredients</Text>
          <View style={styles.tagRow}>
            {product.ingredients.map((ing) => (
              <Badge
                key={ing}
                label={ing}
                color={colors.textSecondary}
                backgroundColor={colors.surfaceVariant}
                size="sm"
              />
            ))}
          </View>
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
    paddingBottom: theme.spacing.xxl,
  },
  image: {
    width: "100%",
    height: 300,
    backgroundColor: colors.surfaceVariant,
  },
  imagePlaceholder: {
    width: "100%",
    height: 200,
    backgroundColor: colors.surfaceVariant,
    justifyContent: "center",
    alignItems: "center",
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    padding: theme.spacing.md,
  },
  headerLeft: {
    flex: 1,
    marginRight: theme.spacing.sm,
  },
  brand: {
    fontSize: theme.fontSize.xs,
    fontWeight: theme.fontWeight.medium,
    color: colors.textTertiary,
    textTransform: "uppercase",
  },
  name: {
    fontSize: theme.fontSize.xl,
    fontWeight: theme.fontWeight.bold,
    color: colors.textPrimary,
    marginTop: 4,
  },
  favoriteButton: {
    padding: 8,
  },
  priceSection: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    paddingHorizontal: theme.spacing.md,
    marginBottom: theme.spacing.sm,
  },
  price: {
    fontSize: theme.fontSize.xl,
    fontWeight: theme.fontWeight.bold,
    color: colors.primaryDark,
  },
  originalPrice: {
    fontSize: theme.fontSize.md,
    color: colors.textTertiary,
    textDecorationLine: "line-through",
  },
  metaRow: {
    paddingHorizontal: theme.spacing.md,
    marginBottom: theme.spacing.md,
  },
  rating: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  ratingText: {
    fontSize: theme.fontSize.sm,
    fontWeight: theme.fontWeight.semibold,
    color: colors.textPrimary,
    marginLeft: 4,
  },
  reviewCount: {
    fontSize: theme.fontSize.sm,
    color: colors.textTertiary,
  },
  infoRow: {
    flexDirection: "row",
    gap: theme.spacing.md,
    paddingHorizontal: theme.spacing.md,
    marginBottom: theme.spacing.md,
  },
  infoItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  infoText: {
    fontSize: theme.fontSize.sm,
    color: colors.textSecondary,
  },
  tagSection: {
    paddingHorizontal: theme.spacing.md,
    marginBottom: theme.spacing.md,
  },
  tagLabel: {
    fontSize: theme.fontSize.sm,
    fontWeight: theme.fontWeight.semibold,
    color: colors.textPrimary,
    marginBottom: 8,
  },
  tagRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  empty: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  emptyText: {
    fontSize: theme.fontSize.md,
    color: colors.textTertiary,
  },
});
