import { useState, useEffect, useCallback } from "react";
import { ScanHistoryItem, AnalysisResult } from "../types";
import { getHistory, addToHistory, removeFromHistory, clearHistory } from "../utils/storage";

export function useHistory() {
  const [history, setHistory] = useState<ScanHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    const data = await getHistory();
    setHistory(data);
    setLoading(false);
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const addScan = useCallback(
    async (result: AnalysisResult) => {
      const item: ScanHistoryItem = {
        id: result.id,
        condition: result.detected_condition,
        skin_type: result.skin_type || "Unknown",
        date: new Date().toISOString(),
        result,
      };
      await addToHistory(item);
      await loadHistory();
    },
    [loadHistory]
  );

  const removeScan = useCallback(
    async (id: string) => {
      await removeFromHistory(id);
      await loadHistory();
    },
    [loadHistory]
  );

  const clearAll = useCallback(async () => {
    await clearHistory();
    setHistory([]);
  }, []);

  return { history, loading, addScan, removeScan, clearAll };
}
