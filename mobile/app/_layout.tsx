import React, { useEffect, useState } from "react";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";
import * as SplashScreen from "expo-splash-screen";
import { colors } from "../constants/colors";
import { loadAppFonts } from "../constants/fonts";

SplashScreen.preventAutoHideAsync().catch(() => {});

export default function RootLayout() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        await loadAppFonts();
      } catch (e) {
        console.warn("Font load failed, falling back to system:", e);
      } finally {
        setReady(true);
        SplashScreen.hideAsync().catch(() => {});
      }
    })();
  }, []);

  if (!ready) return null;

  return (
    <SafeAreaProvider>
      <StatusBar style="dark" />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: colors.background },
        }}
      >
        <Stack.Screen name="(tabs)" />
        <Stack.Screen
          name="analysis/[id]"
          options={{
            headerShown: true,
            headerTitle: "Prescription",
            headerTintColor: colors.textPrimary,
            headerStyle: { backgroundColor: colors.background },
            headerShadowVisible: false,
            presentation: "card",
          }}
        />
        <Stack.Screen
          name="product/[id]"
          options={{
            headerShown: true,
            headerTitle: "Label",
            headerTintColor: colors.textPrimary,
            headerStyle: { backgroundColor: colors.background },
            headerShadowVisible: false,
            presentation: "card",
          }}
        />
        <Stack.Screen
          name="condition/[name]"
          options={{
            headerShown: true,
            headerTitle: "Monograph",
            headerTintColor: colors.textPrimary,
            headerStyle: { backgroundColor: colors.background },
            headerShadowVisible: false,
            presentation: "card",
          }}
        />
      </Stack>
    </SafeAreaProvider>
  );
}
