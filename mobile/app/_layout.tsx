import React from "react";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { colors } from "../constants/colors";

export default function RootLayout() {
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
            headerTitle: "Analysis Results",
            headerTintColor: colors.primaryDark,
            headerStyle: { backgroundColor: colors.background },
            headerShadowVisible: false,
            presentation: "card",
          }}
        />
        <Stack.Screen
          name="product/[id]"
          options={{
            headerShown: true,
            headerTitle: "Product Details",
            headerTintColor: colors.primaryDark,
            headerStyle: { backgroundColor: colors.background },
            headerShadowVisible: false,
            presentation: "card",
          }}
        />
        <Stack.Screen
          name="condition/[name]"
          options={{
            headerShown: true,
            headerTitle: "Condition Info",
            headerTintColor: colors.primaryDark,
            headerStyle: { backgroundColor: colors.background },
            headerShadowVisible: false,
            presentation: "card",
          }}
        />
      </Stack>
    </SafeAreaProvider>
  );
}
