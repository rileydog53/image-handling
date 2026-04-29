import { useCallback, useEffect, useRef, useState } from "react";
import type { ParsedReminder } from "../types";

export function useLiveParse(text: string) {
  const [parsed, setParsed] = useState<ParsedReminder | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortController = useRef<AbortController | null>(null);
  const isLoadingRef = useRef(false);

  const fetchParse = useCallback(async (input: string) => {
    if (abortController.current) abortController.current.abort();
    abortController.current = new AbortController();

    isLoadingRef.current = true;
    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
        signal: abortController.current.signal,
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data: ParsedReminder = await res.json();
      setParsed(data);
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") return;
      setError(err instanceof Error ? err.message : "Parse failed");
    } finally {
      isLoadingRef.current = false;
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (debounceTimer.current) clearTimeout(debounceTimer.current);

    if (!text.trim()) {
      setParsed(null);
      setError(null);
      if (abortController.current) abortController.current.abort();
      return;
    }

    debounceTimer.current = setTimeout(() => {
      if (!isLoadingRef.current) fetchParse(text);
    }, 1000);

    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, [text, fetchParse]);

  return { parsed, isLoading, error };
}
