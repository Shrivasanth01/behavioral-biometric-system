'use client';

import { useState, useCallback } from 'react';
import { apiRequest } from '@/lib/api';
import type { ApiResponse } from '@/types';

interface UseApiState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}

interface UseApiReturn<T> extends UseApiState<T> {
  execute: (...args: unknown[]) => Promise<ApiResponse<T> | null>;
  reset: () => void;
  setData: (data: T | null) => void;
}

export function useApi<T = unknown>(
  initialData: T | null = null
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: initialData,
    isLoading: false,
    error: null,
  });

  const execute = useCallback(async (...args: unknown[]) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      if (typeof args[0] === 'function') {
        const apiCall = args[0] as () => Promise<ApiResponse<T>>;
        const response = await apiCall();
        if (response.success && response.data) {
          setState({ data: response.data, isLoading: false, error: null });
        } else {
          setState({ data: null, isLoading: false, error: response.error || 'An error occurred' });
        }
        return response;
      }
      return null;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'An unexpected error occurred';
      setState({ data: null, isLoading: false, error: message });
      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ data: initialData, isLoading: false, error: null });
  }, [initialData]);

  const setData = useCallback((data: T | null) => {
    setState(prev => ({ ...prev, data }));
  }, []);

  return {
    ...state,
    execute,
    reset,
    setData,
  };
}
