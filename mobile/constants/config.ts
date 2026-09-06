import { Platform } from "react-native";
import Constants from "expo-constants";

/** LAN IP of the Metro dev server (e.g. "192.168.1.4" from "192.168.1.4:8081"), null in prod builds. */
function metroLanHost(): string | null {
  const hostUri = (Constants.expoConfig as { hostUri?: string } | undefined)?.hostUri;
  if (typeof hostUri === "string" && hostUri.includes(":")) {
    const host = hostUri.split(":")[0];
    if (host && host !== "localhost" && host !== "127.0.0.1") return host;
  }
  return null;
}

function defaultBaseUrl(): string {
  const lan = metroLanHost();
  // Physical phones can't reach localhost — point at the dev machine's LAN IP automatically.
  if (lan) return `http://${lan}:8000`;
  return Platform.OS === "android" ? "http://10.0.2.2:8000" : "http://localhost:8000";
}

// ponytail: derived LAN IP, per-emulator override if a platform default ever misfires.
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || defaultBaseUrl();
