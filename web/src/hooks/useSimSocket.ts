import { useCallback, useEffect, useRef, useState } from "react";
import type { ClientMsg, HelloMsg, ServerMsg, StateMsg } from "@/lib/types";

export const HISTORY_LEN = 120; // ~4 s ở 30 Hz
export const CHART_LEGS = [0, 1, 5] as const;

export interface HistoryPoint {
  t: number;
  l0: number;
  l1: number;
  l5: number;
}

export type ConnStatus = "connecting" | "open" | "closed";

/** Kết nối WebSocket tới server Python, tự kết nối lại; state 30 Hz giữ trong ref, UI cập nhật 10 Hz. */
export function useSimSocket(uiHz = 10) {
  const wsRef = useRef<WebSocket | null>(null);
  const stateRef = useRef<StateMsg | null>(null);
  const historyRef = useRef<HistoryPoint[]>([]);
  const [hello, setHello] = useState<HelloMsg | null>(null);
  const [state, setState] = useState<StateMsg | null>(null);
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [status, setStatus] = useState<ConnStatus>("connecting");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let closed = false;
    let retry = 500;
    let timer: number | undefined;

    const connect = () => {
      const proto = location.protocol === "https:" ? "wss:" : "ws:";
      const url = import.meta.env.VITE_WS_URL ?? `${proto}//${location.host}/ws`;
      const ws = new WebSocket(url);
      wsRef.current = ws;
      setStatus("connecting");
      ws.onopen = () => {
        retry = 500;
        setStatus("open");
      };
      ws.onmessage = (ev) => {
        const msg = JSON.parse(ev.data) as ServerMsg;
        if (msg.type === "hello") setHello(msg);
        else if (msg.type === "error") setError(msg.message);
        else if (msg.type === "state") {
          const prev = stateRef.current;
          stateRef.current = msg;
          if (!prev || msg.t !== prev.t) {
            if (prev && msg.t < prev.t) historyRef.current = []; // reset
            const h = historyRef.current;
            h.push({ t: msg.t, l0: msg.q[0][1], l1: msg.q[1][1], l5: msg.q[5][1] });
            if (h.length > HISTORY_LEN) h.splice(0, h.length - HISTORY_LEN);
          }
        }
      };
      ws.onclose = () => {
        setStatus("closed");
        if (closed) return;
        timer = window.setTimeout(connect, retry);
        retry = Math.min(retry * 2, 5000);
      };
    };
    connect();
    return () => {
      closed = true;
      window.clearTimeout(timer);
      wsRef.current?.close();
    };
  }, []);

  useEffect(() => {
    const id = window.setInterval(() => {
      if (stateRef.current) setState(stateRef.current);
      setHistory(historyRef.current.slice());
    }, 1000 / uiHz);
    return () => window.clearInterval(id);
  }, [uiHz]);

  const send = useCallback((msg: ClientMsg) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(msg));
  }, []);

  return { hello, state, stateRef, history, status, error, clearError: () => setError(null), send };
}
