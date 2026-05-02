// ─────────────────────────────────────────────
// hooks/useLiveParse.ts — Live AI parsing as you type
//
// A React "hook" is a reusable piece of logic you can plug into any component.
// This one watches the text box and calls the backend /parse endpoint
// after you pause typing, then returns the parsed result for the preview card.
//
// Key mechanisms:
//   Debounce — waits 1 second after you stop typing before firing
//   In-flight guard — skips the next call if one is already running
//   AbortController — cancels any pending request if the text is cleared
// ─────────────────────────────────────────────

import { useCallback, useEffect, useRef, useState } from "react";
import type { ParsedReminder } from "../types";

export function useLiveParse(text: string) {
  // The parsed reminder returned by Gemini (null if nothing parsed yet)
  const [parsed, setParsed] = useState<ParsedReminder | null>(null);

  // True while a request to /parse is in-flight
  const [isLoading, setIsLoading] = useState(false);

  // Any error message to show the user (null if no error)
  const [error, setError] = useState<string | null>(null);

  // useRef stores a value that persists across renders but doesn't trigger re-renders.
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortController = useRef<AbortController | null>(null); // lets us cancel in-flight fetches
  const isLoadingRef = useRef(false); // ref version of isLoading for use inside callbacks


  // The actual function that calls /parse.
  // Wrapped in useCallback so it doesn't get recreated on every render.
  const fetchParse = useCallback(async (input: string) => {
    // Cancel any previous in-flight request — we only care about the latest text.
    if (abortController.current) abortController.current.abort();
    abortController.current = new AbortController();

    // Mark as loading in both state (triggers re-render) and ref (readable in timers)
    isLoadingRef.current = true;
    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
        signal: abortController.current.signal, // lets us cancel this request
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const data: ParsedReminder = await res.json();
      setParsed(data); // update the preview card with the new result
    } catch (err: unknown) {
      // AbortError means we cancelled the request intentionally — not a real error.
      if (err instanceof Error && err.name === "AbortError") return;
      setError(err instanceof Error ? err.message : "Parse failed");
    } finally {
      // Always reset loading state when done, even if there was an error.
      isLoadingRef.current = false;
      setIsLoading(false);
    }
  }, []);


  // This runs every time `text` changes (i.e. every keystroke).
  useEffect(() => {
    // Cancel any pending debounce timer — we restart the countdown on each keystroke.
    if (debounceTimer.current) clearTimeout(debounceTimer.current);

    // If the box was cleared, reset everything and cancel any in-flight request.
    if (!text.trim()) {
      setParsed(null);
      setError(null);
      if (abortController.current) abortController.current.abort();
      return;
    }

    // Start a 1-second countdown. Only fires if the user stops typing for 1 full second.
    debounceTimer.current = setTimeout(() => {
      // In-flight guard: skip if a request is already running.
      // This prevents piling up requests faster than Gemini can answer.
      if (!isLoadingRef.current) fetchParse(text);
    }, 1000);

    // Cleanup: if the component unmounts, clear the timer to avoid memory leaks.
    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, [text, fetchParse]);

  return { parsed, isLoading, error };
}
