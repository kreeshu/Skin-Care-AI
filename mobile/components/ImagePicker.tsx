import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import * as ImagePicker from "expo-image-picker";
import { colors } from "../constants/colors";
import { theme } from "../constants/theme";

interface ImagePickerProps {
  imageUri: string | null;
  onImageSelected: (uri: string) => void;
}

export function ImagePickerComponent({ imageUri, onImageSelected }: ImagePickerProps) {
  const pickImage = async (useCamera: boolean) => {
    const permissionMethod = useCamera
      ? ImagePicker.requestCameraPermissionsAsync
      : ImagePicker.requestMediaLibraryPermissionsAsync;

    const { status } = await permissionMethod();
    if (status !== "granted") return;

    const launcher = useCamera ? ImagePicker.launchCameraAsync : ImagePicker.launchImageLibraryAsync;

    const result = await launcher({
      mediaTypes: ["images"],
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      onImageSelected(result.assets[0].uri);
    }
  };

  if (imageUri) {
    return (
      <View style={styles.filed}>
        <Ionicons name="checkmark-circle" size={20} color={colors.dispensary} />
        <Text style={styles.filedText}>Photo filed · ready to analyze</Text>
        <TouchableOpacity onPress={() => onImageSelected("")} hitSlop={8}>
          <Text style={styles.replace}>Replace</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.options}>
        <TouchableOpacity style={styles.option} onPress={() => pickImage(true)} activeOpacity={0.8}>
          <Ionicons name="camera-outline" size={26} color={colors.pine} />
          <Text style={styles.optionTitle}>Take photo</Text>
          <Text style={styles.optionSub}>Daylight, no filter</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.option} onPress={() => pickImage(false)} activeOpacity={0.8}>
          <Ionicons name="folder-open-outline" size={26} color={colors.pine} />
          <Text style={styles.optionTitle}>Upload</Text>
          <Text style={styles.optionSub}>From your gallery</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: theme.spacing.md,
  },
  options: {
    flexDirection: "row",
    gap: theme.spacing.sm,
  },
  option: {
    flex: 1,
    backgroundColor: colors.sage,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    alignItems: "flex-start",
    gap: 4,
    borderWidth: 1,
    borderColor: colors.line,
  },
  optionTitle: {
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.md,
    color: colors.textPrimary,
    marginTop: 8,
  },
  optionSub: {
    fontFamily: theme.fontFamily.mono,
    fontSize: 10,
    letterSpacing: 0.6,
    textTransform: "uppercase" as const,
    color: colors.textSecondary,
  },
  filed: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.dispensary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.sm,
    marginBottom: theme.spacing.md,
  },
  filedText: {
    flex: 1,
    fontFamily: theme.fontFamily.mono,
    fontSize: 11,
    letterSpacing: 0.4,
    color: colors.textPrimary,
    textTransform: "uppercase" as const,
  },
  replace: {
    fontFamily: theme.fontFamily.bodySemi,
    fontSize: theme.fontSize.sm,
    color: colors.dispensary,
  },
});
