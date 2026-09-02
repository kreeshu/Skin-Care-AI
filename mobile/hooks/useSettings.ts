import { useState, useEffect, useCallback } from "react";
import { getSettings, saveSettings, AppSettings } from "../utils/storage";

export function useSettings() {
  const [settings, setSettings] = useState<AppSettings>({
    useSlm: false,
    skinTypePreference: null,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const data = await getSettings();
      setSettings(data);
      setLoading(false);
    })();
  }, []);

  const update = useCallback(async (partial: Partial<AppSettings>) => {
    await saveSettings(partial);
    setSettings((prev) => ({ ...prev, ...partial }));
  }, []);

  return { settings, loading, update };
}
