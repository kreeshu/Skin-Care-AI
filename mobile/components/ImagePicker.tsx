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

    const launcher = useCamera
      ? ImagePicker.launchCameraAsync
      : ImagePicker.launchImageLibraryAsync;

    const result = await launcher({
      mediaTypes: ["images"],
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      onImageSelected(result.assets[0].uri);
    }
  };

  return (
    <View style={styles.container}>
      {imageUri ? (
        <View style={styles.previewContainer}>
          <View style={styles.preview}>
            <Ionicons name="image" size={48} color={colors.primary} />
            <Text style={styles.previewText}>Image selected</Text>
          </View>
        </View>
      ) : (
        <View style={styles.options}>
          <TouchableOpacity
            style={styles.option}
            onPress={() => pickImage(true)}
            activeOpacity={0.7}
          >
            <View style={styles.iconContainer}>
              <Ionicons name="camera" size={32} color={colors.primary} />
            </View>
            <Text style={styles.optionTitle}>Take Photo</Text>
            <Text style={styles.optionSubtitle}>Use your camera</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.option}
            onPress={() => pickImage(false)}
            activeOpacity={0.7}
          >
            <View style={styles.iconContainer}>
              <Ionicons name="images" size={32} color={colors.primary} />
            </View>
            <Text style={styles.optionTitle}>Choose Photo</Text>
            <Text style={styles.optionSubtitle}>From your gallery</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: theme.spacing.md,
  },
  options: {
    flexDirection: "row",
    gap: theme.spacing.md,
  },
  option: {
    flex: 1,
    backgroundColor: colors.surfaceVariant,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    alignItems: "center",
    borderWidth: 2,
    borderStyle: "dashed",
    borderColor: colors.border,
  },
  iconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: colors.primaryLight,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: theme.spacing.sm,
  },
  optionTitle: {
    fontSize: theme.fontSize.md,
    fontWeight: theme.fontWeight.semibold,
    color: colors.textPrimary,
  },
  optionSubtitle: {
    fontSize: theme.fontSize.xs,
    color: colors.textTertiary,
    marginTop: 2,
  },
  previewContainer: {
    alignItems: "center",
  },
  preview: {
    width: "100%",
    height: 200,
    backgroundColor: colors.surfaceVariant,
    borderRadius: theme.borderRadius.lg,
    justifyContent: "center",
    alignItems: "center",
    borderWidth: 2,
    borderColor: colors.primary,
    borderStyle: "solid",
  },
  previewText: {
    marginTop: theme.spacing.sm,
    fontSize: theme.fontSize.sm,
    color: colors.primary,
    fontWeight: theme.fontWeight.medium,
  },
});
