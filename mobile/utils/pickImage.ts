import * as ImagePicker from "expo-image-picker";

export interface PickedSkinImage {
  uri: string;
  fileSize?: number;
  mimeType?: string;
}

/** Camera/gallery pick for skin photos. Returns asset info or null (denied/cancelled). */
export async function pickSkinImage(source: "camera" | "gallery"): Promise<PickedSkinImage | null> {
  const { status } = await (source === "camera"
    ? ImagePicker.requestCameraPermissionsAsync()
    : ImagePicker.requestMediaLibraryPermissionsAsync());
  if (status !== "granted") return null;

  const result = await (source === "camera"
    ? ImagePicker.launchCameraAsync
    : ImagePicker.launchImageLibraryAsync)({
    mediaTypes: ["images"],
    allowsEditing: true,
    aspect: [4, 3],
    quality: 0.8,
  });
  if (result.canceled || !result.assets[0]) return null;
  const asset = result.assets[0];
  return { uri: asset.uri, fileSize: asset.fileSize, mimeType: asset.mimeType };
}
