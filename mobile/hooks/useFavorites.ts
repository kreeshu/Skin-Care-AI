import { useState, useCallback } from "react";
import { useFocusEffect } from "expo-router";
import { getFavorites, toggleFavorite } from "../utils/storage";

export function useFavorites() {
  const [favorites, setFavorites] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  const loadFavorites = useCallback(async () => {
    setLoading(true);
    const data = await getFavorites();
    setFavorites(data);
    setLoading(false);
  }, []);

  // Tabs stay mounted; reload on focus so other screens' writes show up.
  useFocusEffect(
    useCallback(() => {
      loadFavorites();
    }, [loadFavorites])
  );

  const toggle = useCallback(
    async (productId: string) => {
      const isFav = await toggleFavorite(productId);
      await loadFavorites();
      return isFav;
    },
    [loadFavorites]
  );

  const isFav = useCallback(
    (productId: string) => favorites.includes(productId),
    [favorites]
  );

  return { favorites, loading, toggle, isFav };
}
