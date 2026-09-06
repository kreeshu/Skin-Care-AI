import React, { useMemo, useRef, useState } from "react";
import { View, StyleSheet, FlatList, TextInput, TouchableOpacity, ActivityIndicator, Image, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { colors } from "../../constants/colors";
import { theme } from "../../constants/theme";
import { Eyebrow, DisplayLg, BodySm, Body } from "../../components/ui/Typography";
import { ConditionBadge } from "../../components/ConditionBadge";
import { api } from "../../services/api";
import { toUserMessage } from "../../services/apiError";
import { useHistory } from "../../hooks/useHistory";
import { useSettings } from "../../hooks/useSettings";
import { pickSkinImage, PickedSkinImage } from "../../utils/pickImage";
import { ChatTurn, AnalysisResult } from "../../types";

const QUICK_REPLIES = ["Explain my result", "Compare my top 2 cleansers", "Build my AM/PM routine"];

function contextFromResult(result?: AnalysisResult) {
  if (!result) return undefined;
  const product_ids: string[] = [];
  for (const recs of Object.values(result.recommendations ?? {})) {
    for (const r of (recs ?? []).slice(0, 2)) product_ids.push(r.product_id);
    if (product_ids.length >= 6) break;
  }
  return {
    condition: result.detected_condition,
    skin_type: result.skin_type,
    is_medical: result.is_medical,
    product_ids: product_ids.slice(0, 6),
  };
}

function topPicks(result: AnalysisResult): string[] {
  const names: string[] = [];
  for (const recs of Object.values(result.recommendations ?? {})) {
    for (const r of (recs ?? []).slice(0, 2)) {
      names.push(r.name);
      if (names.length >= 3) return names;
    }
  }
  return names;
}

function ResultCard({ result, onPress }: { result: AnalysisResult; onPress: () => void }) {
  const serious = result.is_medical && result.detected_condition?.toLowerCase() === "carcinoma";
  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.8} accessibilityRole="button">
      <Eyebrow>Your result · tap for details</Eyebrow>
      <View style={styles.cardHead}>
        <ConditionBadge condition={result.detected_condition} size="sm" />
        <BodySm style={styles.muted}>{Math.round(result.condition_confidence * 100)}% reading</BodySm>
      </View>
      {result.skin_type ? (
        <BodySm style={styles.muted}>
          {result.skin_type} · {Math.round(result.skin_type_confidence * 100)}% skin type
        </BodySm>
      ) : null}
      {topPicks(result).map((name) => (
        <BodySm key={name} numberOfLines={1} style={styles.pick}>• {name}</BodySm>
      ))}
      {serious ? (
        <BodySm style={styles.warn}>Needs a dermatologist promptly — this app does not diagnose.</BodySm>
      ) : null}
    </TouchableOpacity>
  );
}

export default function ChatScreen() {
  const { history, addScan } = useHistory();
  const { settings } = useSettings();
  const router = useRouter();
  const [messages, setMessages] = useState<ChatTurn[]>([]);
  const [activeResult, setActiveResult] = useState<AnalysisResult | null>(null);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [photoBusy, setPhotoBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const listRef = useRef<FlatList>(null);

  const context = useMemo(
    () => contextFromResult(activeResult ?? history[0]?.result),
    [activeResult, history]
  );

  const textHistory = (turns: ChatTurn[]) => {
    const out: { role: string; content: string }[] = [];
    for (const t of turns) {
      if ("content" in t && t.content) out.push({ role: t.role, content: t.content });
    }
    return out.slice(-10);
  };

  const send = async (text: string) => {
    const message = text.trim();
    if (!message || sending) return;
    setError(null);
    const next: ChatTurn[] = [...messages, { role: "user", content: message }];
    setMessages(next);
    setInput("");
    setSending(true);
    try {
      const res = await api.sendChatMessage(message, textHistory(next), context);
      setMessages([...next, { role: "assistant", content: res.reply }]);
    } catch (e: any) {
      setError(e?.message ?? "Chat failed. Is the backend running?");
    } finally {
      setSending(false);
    }
  };

  const markPhoto = (uri: string, status: "done" | "error") =>
    setMessages((prev) =>
      prev.map((m) =>
        "kind" in m && m.kind === "photo" && m.imageUri === uri ? { ...m, status } : m
      )
    );

  const analyzePhoto = async (photo: PickedSkinImage) => {
    const uri = photo.uri;
    setPhotoBusy(true);
    setError(null);
    try {
      const result = (await api.analyzeImage(uri, settings.useSlm, photo)) as AnalysisResult;
      await addScan(result);
      setActiveResult(result);
      markPhoto(uri, "done");
      setMessages((prev) => [...prev, { role: "assistant", kind: "result", result }]);
    } catch (e: any) {
      console.log("[analyze] upload failed:", e?.kind ?? "", e?.url ?? "", e?.message ?? e);
      markPhoto(uri, "error");
      const { title, message } = toUserMessage(e);
      setError(`${title}: ${message}`);
    } finally {
      setPhotoBusy(false);
    }
  };

  const pickThenAnalyze = async (source: "camera" | "gallery") => {
    const photo = await pickSkinImage(source);
    if (!photo) return;
    const uri = photo.uri;
    setMessages((prev) => [...prev, { role: "user", kind: "photo", imageUri: uri, status: "analyzing", fileSize: photo.fileSize, mimeType: photo.mimeType }]);
    await analyzePhoto(photo);
  };

  const onPlus = () => {
    if (photoBusy) return;
    Alert.alert("Add a skin photo", "One clear photo in daylight.", [
      { text: "Take photo", onPress: () => pickThenAnalyze("camera") },
      { text: "Upload", onPress: () => pickThenAnalyze("gallery") },
      { text: "Cancel", style: "cancel" },
    ]);
  };

  const renderItem = ({ item }: { item: ChatTurn }) => {
    if ("content" in item) {
      const isUser = item.role === "user";
      return (
        <View style={[styles.bubble, isUser ? styles.user : styles.ai]}>
          <Body style={isUser ? styles.userText : undefined}>{item.content}</Body>
        </View>
      );
    }
    if (item.kind === "photo") {
      const failed = item.status === "error";
      return (
        <TouchableOpacity
          style={[styles.bubble, styles.user, styles.photoBubble]}
          disabled={!failed || photoBusy}
          onPress={() => analyzePhoto({ uri: item.imageUri, fileSize: item.fileSize, mimeType: item.mimeType })}
          activeOpacity={0.8}
        >
          <Image source={{ uri: item.imageUri }} style={styles.photo} />
          {item.status === "analyzing" ? (
            <View style={styles.photoOverlay}>
              <ActivityIndicator color={colors.white} size="small" />
              <BodySm style={styles.userText}>Checking…</BodySm>
            </View>
          ) : null}
          {failed ? <BodySm style={styles.userText}>Check failed — tap to retry</BodySm> : null}
        </TouchableOpacity>
      );
    }
    return (
      <ResultCard
        result={item.result}
        onPress={() =>
          router.push({
            pathname: "/analysis/[id]",
            params: { id: item.result.id, result: JSON.stringify(item.result) },
          })
        }
      />
    );
  };

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      <View style={styles.header}>
        <View style={styles.headerText}>
          <Eyebrow>Skin chat{context ? ` · ${context.condition} · ${context.skin_type}` : ""}</Eyebrow>
          <DisplayLg>Ask about your skin.</DisplayLg>
        </View>
      </View>

      <FlatList
        ref={listRef}
        data={messages}
        keyExtractor={(_, i) => String(i)}
        contentContainerStyle={styles.list}
        onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: true })}
        ListEmptyComponent={
          <View style={styles.empty}>
            <BodySm style={styles.emptyText}>
              Tap + to check a skin photo, or just ask about products, routines and ingredients.
            </BodySm>
            {QUICK_REPLIES.map((q) => (
              <TouchableOpacity key={q} style={styles.chip} onPress={() => send(q)} activeOpacity={0.75}>
                <BodySm style={styles.chipText}>{q}</BodySm>
              </TouchableOpacity>
            ))}
          </View>
        }
        renderItem={renderItem}
      />

      {error ? (
        <TouchableOpacity onPress={() => setError(null)} style={styles.error}>
          <BodySm style={styles.errorText}>{error}</BodySm>
        </TouchableOpacity>
      ) : null}
      {context?.is_medical ? (
        <BodySm style={styles.warn}>Possible medical condition — please see a dermatologist.</BodySm>
      ) : null}

      <View style={styles.inputRow}>
        <TouchableOpacity
          style={[styles.plus, photoBusy && styles.sendDisabled]}
          onPress={onPlus}
          disabled={photoBusy}
          accessibilityRole="button"
          accessibilityLabel="Add a skin photo"
        >
          {photoBusy ? (
            <ActivityIndicator color={colors.white} size="small" />
          ) : (
            <Ionicons name="add" size={22} color={colors.white} />
          )}
        </TouchableOpacity>
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="Ask or tap + to check a photo…"
          placeholderTextColor={colors.textTertiary}
          multiline
          editable={!sending}
          onSubmitEditing={() => send(input)}
        />
        <TouchableOpacity
          style={[styles.send, sending && styles.sendDisabled]}
          onPress={() => send(input)}
          disabled={sending || !input.trim()}
          accessibilityRole="button"
          accessibilityLabel="Send message"
        >
          {sending ? (
            <ActivityIndicator color={colors.white} size="small" />
          ) : (
            <Ionicons name="send" size={18} color={colors.white} />
          )}
        </TouchableOpacity>
      </View>
      <BodySm style={styles.disclaimer}>Cosmetic advice only — not medical advice.</BodySm>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  header: { paddingHorizontal: theme.spacing.md, paddingTop: theme.spacing.sm },
  headerText: { gap: theme.spacing.xs2 },
  list: { padding: theme.spacing.md, gap: theme.spacing.sm, paddingBottom: 8 },
  empty: { gap: theme.spacing.sm },
  emptyText: { color: colors.textSecondary },
  chip: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.sm,
  },
  chipText: { color: colors.dispensary },
  bubble: {
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.sm,
    maxWidth: "85%",
  },
  user: { alignSelf: "flex-end", backgroundColor: colors.dispensary },
  ai: { alignSelf: "flex-start", backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.line },
  userText: { color: colors.white },
  photoBubble: { padding: 6, gap: 4 },
  photo: { width: 200, height: 150, borderRadius: theme.borderRadius.md },
  photoOverlay: { flexDirection: "row", alignItems: "center", gap: 6 },
  card: {
    alignSelf: "flex-start",
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.sm,
    gap: 4,
    maxWidth: "90%",
  },
  cardHead: { flexDirection: "row", alignItems: "center", gap: 8 },
  muted: { color: colors.textSecondary },
  pick: { color: colors.textPrimary },
  error: { marginHorizontal: theme.spacing.md, marginBottom: 4 },
  errorText: { color: colors.oxblood },
  warn: { marginHorizontal: theme.spacing.md, marginBottom: 4, color: colors.oxblood },
  inputRow: {
    flexDirection: "row",
    alignItems: "flex-end",
    gap: theme.spacing.sm,
    padding: theme.spacing.md,
    paddingTop: theme.spacing.sm,
  },
  input: {
    flex: 1,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.sm,
    maxHeight: 110,
    color: colors.textPrimary,
  },
  plus: {
    backgroundColor: colors.dispensary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.sm,
  },
  send: {
    backgroundColor: colors.dispensary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.sm,
  },
  sendDisabled: { opacity: 0.5 },
  disclaimer: { textAlign: "center", color: colors.textTertiary, paddingBottom: theme.spacing.sm },
});
