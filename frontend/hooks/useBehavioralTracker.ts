'use client';

import { useEffect, useRef, useCallback } from 'react';
import { BEHAVIORAL_UPLOAD_INTERVAL } from '@/lib/constants';
import { api } from '@/lib/api';
import { getAccessToken } from '@/lib/api';
import type { BehavioralEvent } from '@/types';

interface TrackerOptions {
  userId?: string;
  sessionId: string;
  enabled?: boolean;
}

export function useBehavioralTracker(options: TrackerOptions) {
  const { userId, sessionId, enabled = true } = options;
  const eventsRef = useRef<BehavioralEvent[]>([]);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const trackerRef = useRef<{ sendEvent: (type: string, data: Record<string, unknown>) => void; destroy: () => void } | null>(null);

  const sendEvent = useCallback((type: string, data: Record<string, unknown>) => {
    const event: BehavioralEvent = {
      type,
      timestamp: Date.now(),
      data,
      sessionId,
      userId,
    };
    eventsRef.current.push(event);
  }, [sessionId, userId]);

  const flushEvents = useCallback(async () => {
    if (eventsRef.current.length === 0) return;
    const events = eventsRef.current.splice(0, 100);
    try {
      await api.behavioral.uploadEvents(events);
    } catch {
      eventsRef.current.unshift(...events);
    }
  }, []);

  useEffect(() => {
    if (!enabled) return;

    const interval = setInterval(flushEvents, BEHAVIORAL_UPLOAD_INTERVAL);
    intervalRef.current = interval;

    const handleBeforeUnload = () => {
      if (eventsRef.current.length > 0) {
        const payload = JSON.stringify({ events: eventsRef.current });
        navigator.sendBeacon(
          `${process.env.NEXT_PUBLIC_API_URL}/behavioral/events`,
          new Blob([payload], { type: 'application/json' })
        );
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);

    if (typeof window !== 'undefined' && (window as unknown as Record<string, unknown>).BehavioralTracker) {
      const Tracker = (window as unknown as Record<string, unknown>).BehavioralTracker as new (opts: Record<string, unknown>) => { sendEvent: (type: string, data: Record<string, unknown>) => void; destroy: () => void };
      const tracker = new Tracker({
        userId,
        sessionId,
        endpoint: `${process.env.NEXT_PUBLIC_API_URL}/behavioral/events`,
        sampleRate: 50,
        batchSize: 100,
        uploadInterval: BEHAVIORAL_UPLOAD_INTERVAL,
      });
      trackerRef.current = tracker;
    }

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      window.removeEventListener('beforeunload', handleBeforeUnload);
      if (trackerRef.current) {
        trackerRef.current.destroy();
      }
      flushEvents();
    };
  }, [enabled, flushEvents, userId, sessionId]);

  return {
    sendEvent,
    flushEvents,
    getEventCount: () => eventsRef.current.length,
    isTrackerReady: !!trackerRef.current,
  };
}

export function useBehavioralLoginCapture() {
  const captureRef = useRef<{
    start: () => void;
    stop: () => BehavioralEvent[];
  } | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && (window as unknown as Record<string, unknown>).BehavioralTracker) {
      const Tracker = (window as unknown as Record<string, unknown>).BehavioralTracker as unknown as Record<string, unknown>;
      if (typeof (Tracker as Record<string, unknown>).createLoginCapture === 'function') {
        captureRef.current = (Tracker as { createLoginCapture: () => { start: () => void; stop: () => BehavioralEvent[] } }).createLoginCapture();
      }
    }
    return () => {
      captureRef.current = null;
    };
  }, []);

  const startCapture = useCallback(() => {
    captureRef.current?.start();
  }, []);

  const stopCapture = useCallback((): BehavioralEvent[] => {
    return captureRef.current?.stop() || [];
  }, []);

  return { startCapture, stopCapture, isReady: !!captureRef.current };
}
