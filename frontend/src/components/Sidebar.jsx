import { NavLink } from "react-router-dom";
import { ShieldHalf, LayoutGrid, Link2, MessageSquareWarning, FileSearch, History, Radar } from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutGrid, end: true },
  { to: "/url-scanner", label: "URL Scanner", icon: Link2 },
  { to: "/message-analyzer", label: "Message Analyzer", icon: MessageSquareWarning },
  { to: "/file-analyzer", label: "File Analyzer", icon: FileSearch },
  { to: "/history", label: "Scan History", icon: History },
];

export default function Sidebar() {
  return (
    <aside className="hidden md:flex w-64 shrink-0 flex-col border-r border-ink-border bg-ink-panel/60 px-4 py-6">
      <div className="flex items-center gap-2.5 px-2 mb-8">
        <div className="relative flex h-9 w-9 items-center justify-center rounded-md bg-signal/10 border border-signal/30">
          <ShieldHalf className="h-5 w-5 text-signal" strokeWidth={2} />
        </div>
        <div>
          <p className="font-display text-[15px] font-semibold leading-tight text-ash-50">CyberShield AI</p>
          <p className="text-[11px] text-ash-400 leading-tight">Threat Detection Platform</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `group flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors ${
                isActive
                  ? "bg-signal/10 text-signal border border-signal/25"
                  : "text-ash-200 border border-transparent hover:bg-ink-raised hover:text-ash-50"
              }`
            }
          >
            <Icon className="h-4 w-4 shrink-0" strokeWidth={2} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto rounded-md border border-ink-border bg-ink-raised/50 p-3">
        <div className="flex items-center gap-2 text-verdict-safe text-xs font-medium">
          <Radar className="h-3.5 w-3.5 animate-pulseDot" />
          Detection engine online
        </div>
        <p className="mt-1.5 text-[11px] text-ash-400">Heuristics + ML v1.0.0</p>
      </div>

      <div className="mt-4 px-1">
        <p className="text-[11px] text-ash-600">DevHack IIMTU 2026</p>
        <p className="text-[11px] text-ash-600">Build for Impact</p>
      </div>
    </aside>
  );
}
