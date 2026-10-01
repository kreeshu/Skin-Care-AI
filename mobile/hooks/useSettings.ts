import { useState, useCallback } from "react";
import { useFocusEffect } from "expo-router";
import { getSettings, saveSettings, AppSettings } from "../utils/storage";

export function useSettings() {
  const [settings, setSettings] = useState<AppSettings>({ skinTypePreference: null });
  const [loading, setLoading] = useState(true);

  // Tabs stay mounted; reload on focus so changes made in Settings reach Chat.
  useFocusEffect(
    useCallback(() => {
      getSettings().then((data) => {
        setSettings(data);
        setLoading(false);
      });
    }, [])
  );

  const update = useCallback(async (partial: Partial<AppSettings>) => {
    await saveSettings(partial);
    setSettings((prev) => ({ ...prev, ...partial }));
  }, []);

  return { settings, loading, update };
}
