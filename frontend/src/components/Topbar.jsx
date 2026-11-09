import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Topbar({ title, subtitle }) {
  const [online, setOnline] = useState(null); // null = checking

  useEffect(() => {
    let cancelled = false;
    api
      .get("/api/health")
      .then(() => !cancelled && setOnline(true))
      .catch(() => !cancelled && setOnline(false));
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <header className="flex items-center justify-between border-b border-ink-border bg-ink/80 backdrop-blur px-5 py-4 md:px-8">
      <div>
        <h1 className="font-display text-xl font-semibold text-ash-50">{title}</h1>
        {subtitle && <p className="text-sm text-ash-400 mt-0.5">{subtitle}</p>}
      </div>
      <div
        className={`flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium ${
          online === false
            ? "border-verdict-malicious/40 bg-verdict-maliciousBg text-verdict-malicious"
            : "border-verdict-safe/30 bg-verdict-safeBg text-verdict-safe"
        }`}
      >
        <span
          className={`h-1.5 w-1.5 rounded-full ${
            online === false ? "bg-verdict-malicious" : "bg-verdict-safe animate-pulseDot"
          }`}
        />
        {online === null ? "Connecting…" : online ? "API Connected" : "API Offline"}
      </div>
    </header>
  );
}
