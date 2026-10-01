import * as Font from "expo-font";

export async function loadAppFonts(): Promise<void> {
  await Font.loadAsync({
    "Excon-Regular": require("../assets/fonts/Excon-Regular.ttf"),
    "Excon-Medium": require("../assets/fonts/Excon-Medium.ttf"),
    "Excon-Bold": require("../assets/fonts/Excon-Bold.ttf"),
  });
}
