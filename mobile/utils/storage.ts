import AsyncStorage from "@react-native-async-storage/async-storage";
import { ScanHistoryItem } from "../types";

const HISTORY_KEY = "@skincare_history";
const FAVORITES_KEY = "@skincare_favorites";
const SETTINGS_KEY = "@skincare_settings";

export async function getHistory(): Promise<ScanHistoryItem[]> {
  try {
    const data = await AsyncStorage.getItem(HISTORY_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

export async function addToHistory(item: ScanHistoryItem): Promise<void> {
  const history = await getHistory();
  const updated = [item, ...history].slice(0, 50);
  await AsyncStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
}

export async function removeFromHistory(id: string): Promise<void> {
  const history = await getHistory();
  const updated = history.filter((item) => item.id !== id);
  await AsyncStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
}

export async function clearHistory(): Promise<void> {
  await AsyncStorage.removeItem(HISTORY_KEY);
}

export async function getFavorites(): Promise<string[]> {
  try {
    const data = await AsyncStorage.getItem(FAVORITES_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

export async function toggleFavorite(productId: string): Promise<boolean> {
  const favorites = await getFavorites();
  const index = favorites.indexOf(productId);
  let updated: string[];

  if (index > -1) {
    updated = favorites.filter((id) => id !== productId);
  } else {
    updated = [...favorites, productId];
  }

  await AsyncStorage.setItem(FAVORITES_KEY, JSON.stringify(updated));
  return index === -1;
}

export async function isFavorite(productId: string): Promise<boolean> {
  const favorites = await getFavorites();
  return favorites.includes(productId);
}

export interface AppSettings {
  useSlm: boolean;
  skinTypePreference: string | null;
}

const DEFAULT_SETTINGS: AppSettings = {
  useSlm: false,
  skinTypePreference: null,
};

export async function getSettings(): Promise<AppSettings> {
  try {
    const data = await AsyncStorage.getItem(SETTINGS_KEY);
    return data ? { ...DEFAULT_SETTINGS, ...JSON.parse(data) } : DEFAULT_SETTINGS;
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export async function saveSettings(settings: Partial<AppSettings>): Promise<void> {
  const current = await getSettings();
  const updated = { ...current, ...settings };
  await AsyncStorage.setItem(SETTINGS_KEY, JSON.stringify(updated));
}
