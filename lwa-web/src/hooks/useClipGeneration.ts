'use client';

import { useCallback, useRef, useState } from 'react';
import { generateClips, ApiError } from '@/lib/api';
import type { ClipBatchResponse, GenerateRequest, GenerationState } from '@/lib/types';

const INITIAL_STATE: GenerationState = {
  status: 'idle',
  data: null,
  error: null,
};

export function useClipGeneration() {
  const [state, setState] = useState<GenerationState>(INITIAL_STATE);
  const abortRef = useRef<AbortController | null>(null);

  const generate = useCallback(async (payload: GenerateRequest) => {
    // Cancel any in-flight request
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setState({ status: 'loading', data: null, error: null });

    try {
      const data: ClipBatchResponse = await generateClips(payload, controller.signal);
      setState({ status: 'success', data, error: null });
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        // User cancelled — stay in loading until they try again
        return;
      }
      const message =
        err instanceof ApiError
          ? err.message
          : 'An unexpected error occurred. Please try again.';
      setState({ status: 'error', data: null, error: message });
    }
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setState(INITIAL_STATE);
  }, []);

  return { state, generate, reset };
}
