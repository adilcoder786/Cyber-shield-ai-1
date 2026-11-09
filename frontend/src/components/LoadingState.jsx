import { Loader2 } from "lucide-react";

export default function LoadingState({ message = "Analyzing…" }) {
  return (
    <div className="panel flex flex-col items-center justify-center gap-3 py-14">
      <div className="relative">
        <Loader2 className="h-7 w-7 text-signal animate-spin" />
      </div>
      <p className="text-sm text-ash-200">{message}</p>
      <p className="text-xs text-ash-400">Running heuristic rules + ML model…</p>
    </div>
  );
}
