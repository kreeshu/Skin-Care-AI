import { useCallback, useEffect, useRef, useState } from "react";

interface FetcherState<T> {
  data: T | null;
  loading: boolean;
  error: unknown;
  /** Bump to force a refetch without changing deps. */
  retry: () => void;
  /** Manually re-invoke the fetcher. */
  refetch: () => Promise<void>;
}

interface UseFetcherOptions {
  /** When false, the fetcher does not run on mount. Use when waiting for params. */
  enabled?: boolean;
}

/**
 * Generic data hook. Replaces the copy-pasted `cancelled` / `retryKey` /
 * `loading` / `error` state pattern that lived in 3 screens.
 *
 *   const { data, loading, error, retry } = useFetcher(() => api.getProducts(...), [page]);
 *
 * Aborts on unmount. `retry` bumps an internal key to force a re-run.
 */
export function useFetcher<T>(
  fn: () => Promise<T>,
  deps: React.DependencyList,
  options: UseFetcherOptions = {},
): FetcherState<T> {
  const { enabled = true } = options;
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(enabled);
  const [error, setError] = useState<unknown>(null);
  const [retryKey, setRetryKey] = useState(0);

  // Refs let `fn` and `enabled` update without re-running the effect
  // on every render — only when `deps` or `retryKey` change.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const fnRef = useRef(fn);
  fnRef.current = fn;
  const enabledRef = useRef(enabled);
  enabledRef.current = enabled;

  // Stringify deps so the effect can compare by value even when
  // callers pass inline objects / arrays.
  const depsKey = JSON.stringify(deps);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fnRef.current();
      setData(result);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!enabledRef.current) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    (async () => {
      try {
        const result = await fnRef.current();
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) setError(err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [depsKey, retryKey]);

  const retry = useCallback(() => setRetryKey((k) => k + 1), []);

  return { data, loading, error, retry, refetch };
}
