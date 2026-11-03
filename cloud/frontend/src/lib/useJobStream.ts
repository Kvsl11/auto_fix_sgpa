import { useEffect, useRef, useState } from "react";
import { api, Job, JobStatus, LogEntry, Stats } from "./api";

/** Assina o WebSocket de uma execução e mantém log/status/estatísticas atualizados. */
export function useJobStream(jobId: string | null) {
  const [job, setJob] = useState<Job | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [connected, setConnected] = useState(false);
  const retry = useRef(0);

  useEffect(() => {
    if (!jobId) { setJob(null); setLogs([]); return; }
    let ws: WebSocket | null = null;
    let closed = false;
    let timer: number | undefined;

    const connect = () => {
      ws = new WebSocket(api.wsUrl(jobId));
      ws.onopen = () => { setConnected(true); retry.current = 0; };
      ws.onmessage = (ev) => {
        const msg = JSON.parse(ev.data);
        switch (msg.type) {
          case "snapshot":
            setJob(msg.data as Job);
            setLogs((msg.data as Job).logs ?? []);
            break;
          case "log":
            setLogs((prev) => {
              const next = [...prev, msg.data as LogEntry];
              return next.length > 2000 ? next.slice(-2000) : next;
            });
            break;
          case "status":
            setJob((j) => j && {
              ...j,
              status: msg.data as JobStatus,
              ativo: !["finished", "error"].includes(msg.data),
            });
            break;
          case "stats":
            setJob((j) => j && { ...j, stats: msg.data as Stats });
            break;
        }
      };
      ws.onclose = (ev) => {
        setConnected(false);
        if (closed || ev.code === 4401 || ev.code === 4404) return;
        retry.current += 1;
        timer = window.setTimeout(connect, Math.min(1000 * 2 ** retry.current, 10000));
      };
    };
    connect();
    return () => { closed = true; window.clearTimeout(timer); ws?.close(); };
  }, [jobId]);

  return { job, logs, connected };
}
