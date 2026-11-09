import { NavLink } from "react-router-dom";
import { LayoutGrid, Link2, MessageSquareWarning, FileSearch, History } from "lucide-react";

const ITEMS = [
  { to: "/", label: "Home", icon: LayoutGrid, end: true },
  { to: "/url-scanner", label: "URL", icon: Link2 },
  { to: "/message-analyzer", label: "Message", icon: MessageSquareWarning },
  { to: "/file-analyzer", label: "File", icon: FileSearch },
  { to: "/history", label: "History", icon: History },
];

export default function MobileNav() {
  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-20 flex items-stretch justify-between border-t border-ink-border bg-ink-panel/95 backdrop-blur px-1 py-1.5">
      {ITEMS.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          className={({ isActive }) =>
            `flex flex-1 flex-col items-center gap-1 rounded-md py-1.5 text-[10px] ${
              isActive ? "text-signal" : "text-ash-400"
            }`
          }
        >
          <Icon className="h-4 w-4" strokeWidth={2} />
          {label}
        </NavLink>
      ))}
    </nav>
  );
}
