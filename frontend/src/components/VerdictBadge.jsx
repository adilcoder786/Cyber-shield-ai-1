import { ShieldCheck, ShieldAlert, ShieldX } from "lucide-react";

const CONFIG = {
  safe: {
    label: "Safe",
    icon: ShieldCheck,
    text: "text-verdict-safe",
    bg: "bg-verdict-safeBg",
    border: "border-verdict-safe/30",
  },
  suspicious: {
    label: "Suspicious",
    icon: ShieldAlert,
    text: "text-verdict-suspicious",
    bg: "bg-verdict-suspiciousBg",
    border: "border-verdict-suspicious/30",
  },
  malicious: {
    label: "Malicious",
    icon: ShieldX,
    text: "text-verdict-malicious",
    bg: "bg-verdict-maliciousBg",
    border: "border-verdict-malicious/30",
  },
};

export default function VerdictBadge({ verdict, size = "md" }) {
  const cfg = CONFIG[verdict] || CONFIG.safe;
  const Icon = cfg.icon;
  const padding = size === "lg" ? "px-4 py-2 text-sm" : "px-2.5 py-1 text-xs";
  const iconSize = size === "lg" ? "h-4 w-4" : "h-3.5 w-3.5";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${cfg.text} ${cfg.bg} ${cfg.border} ${padding}`}
    >
      <Icon className={iconSize} strokeWidth={2.2} />
      {cfg.label}
    </span>
  );
}
