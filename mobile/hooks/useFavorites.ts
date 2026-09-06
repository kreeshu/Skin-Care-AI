import { useState, useEffect, useCallback } from "react";
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

  useEffect(() => {
    loadFavorites();
  }, [loadFavorites]);

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
