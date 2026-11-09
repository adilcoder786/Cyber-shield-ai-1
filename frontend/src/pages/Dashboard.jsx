import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar,
} from "recharts";
import {
  ShieldCheck, ShieldX, Activity, Gauge, Link2, MessageSquareWarning, FileSearch, ArrowRight,
} from "lucide-react";
import Topbar from "../components/Topbar";
import StatCard from "../components/StatCard";
import VerdictBadge from "../components/VerdictBadge";
import EmptyState from "../components/EmptyState";
import ErrorBanner from "../components/ErrorBanner";
import { getStats, getHistory } from "../api/client";

const VERDICT_COLORS = { safe: "#33C17E", suspicious: "#E8A93B", malicious: "#E15559" };

const QUICK_ACTIONS = [
  { to: "/url-scanner", label: "Scan a URL", desc: "Check a link before you click it", icon: Link2 },
  { to: "/message-analyzer", label: "Analyze a message", desc: "Spot phishing emails & texts", icon: MessageSquareWarning },
  { to: "/file-analyzer", label: "Scan a file", desc: "Detect disguised or risky files", icon: FileSearch },
];

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recent, setRecent] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [statsData, historyData] = await Promise.all([
          getStats(),
          getHistory({ page: 1, page_size: 5 }),
        ]);
        setStats(statsData);
        setRecent(historyData.items);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const safeRate = stats && stats.total_scans > 0
    ? Math.round((stats.safe_count / stats.total_scans) * 100)
    : 0;

  const verdictPieData = stats
    ? [
        { name: "Safe", value: stats.safe_count, color: VERDICT_COLORS.safe },
        { name: "Suspicious", value: stats.suspicious_count, color: VERDICT_COLORS.suspicious },
        { name: "Malicious", value: stats.malicious_count, color: VERDICT_COLORS.malicious },
      ]
    : [];

  const typeBarData = stats
    ? [
        { name: "URLs", value: stats.scans_by_type.url },
        { name: "Messages", value: stats.scans_by_type.message },
        { name: "Files", value: stats.scans_by_type.file },
      ]
    : [];

  return (
    <div className="flex-1 flex flex-col">
      <Topbar title="Threat Dashboard" subtitle="Real-time overview of scans and detected threats." />
      <div className="flex-1 px-5 md:px-8 py-6 space-y-6">
        <ErrorBanner message={error} />

        {loading ? (
          <div className="panel py-16 text-center text-sm text-ash-400">Loading threat statistics…</div>
        ) : !stats ? (
          <EmptyState
            icon={ShieldX}
            title="Couldn't load the dashboard"
            description="The backend didn't return any data. Make sure the API server is running and VITE_API_URL in frontend/.env points to it."
          />
        ) : (
          <>
            {/* Hero stat strip */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard label="Total Scans" value={stats.total_scans} icon={Activity} accent="text-signal" />
              <StatCard
                label="Threats Blocked"
                value={stats.malicious_count}
                icon={ShieldX}
                accent="text-verdict-malicious"
                sub={`${stats.suspicious_count} more flagged as suspicious`}
              />
              <StatCard label="Safe Rate" value={`${safeRate}%`} icon={ShieldCheck} accent="text-verdict-safe" />
              <StatCard label="Avg Risk Score" value={stats.avg_risk_score} icon={Gauge} accent="text-signal" sub="out of 100" />
            </div>

            {/* Quick actions */}
            <div className="grid sm:grid-cols-3 gap-4">
              {QUICK_ACTIONS.map(({ to, label, desc, icon: Icon }) => (
                <Link
                  key={to}
                  to={to}
                  className="panel p-4 flex items-center gap-3 hover:border-signal/40 transition-colors group"
                >
                  <div className="flex h-9 w-9 items-center justify-center rounded-md bg-signal/10 border border-signal/25 shrink-0">
                    <Icon className="h-4 w-4 text-signal" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-ash-50">{label}</p>
                    <p className="text-xs text-ash-400 truncate">{desc}</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-ash-600 group-hover:text-signal group-hover:translate-x-0.5 transition-all shrink-0" />
                </Link>
              ))}
            </div>

            {/* Charts row */}
            <div className="grid lg:grid-cols-3 gap-4">
              <div className="panel p-4 lg:col-span-2">
                <p className="label-caps mb-3">Threat activity — last 7 days</p>
                <ResponsiveContainer width="100%" height={220}>
                  <AreaChart data={stats.scans_last_7_days}>
                    <defs>
                      <linearGradient id="safeGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={VERDICT_COLORS.safe} stopOpacity={0.4} />
                        <stop offset="95%" stopColor={VERDICT_COLORS.safe} stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="susGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={VERDICT_COLORS.suspicious} stopOpacity={0.4} />
                        <stop offset="95%" stopColor={VERDICT_COLORS.suspicious} stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="malGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={VERDICT_COLORS.malicious} stopOpacity={0.5} />
                        <stop offset="95%" stopColor={VERDICT_COLORS.malicious} stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#212B26" vertical={false} />
                    <XAxis
                      dataKey="date"
                      tickFormatter={(d) => d.slice(5)}
                      stroke="#7C8985"
                      fontSize={11}
                      tickLine={false}
                      axisLine={false}
                    />
                    <YAxis stroke="#7C8985" fontSize={11} tickLine={false} axisLine={false} allowDecimals={false} />
                    <Tooltip
                      contentStyle={{ background: "#111815", border: "1px solid #212B26", borderRadius: 6, fontSize: 12 }}
                      labelStyle={{ color: "#ECEFED" }}
                    />
                    <Area type="monotone" dataKey="safe" stackId="1" stroke={VERDICT_COLORS.safe} fill="url(#safeGrad)" strokeWidth={2} />
                    <Area type="monotone" dataKey="suspicious" stackId="1" stroke={VERDICT_COLORS.suspicious} fill="url(#susGrad)" strokeWidth={2} />
                    <Area type="monotone" dataKey="malicious" stackId="1" stroke={VERDICT_COLORS.malicious} fill="url(#malGrad)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="panel p-4">
                <p className="label-caps mb-3">Verdict breakdown</p>
                {stats.total_scans === 0 ? (
                  <div className="h-[180px] flex items-center justify-center text-xs text-ash-400">No scans yet</div>
                ) : (
                  <>
                    <ResponsiveContainer width="100%" height={160}>
                      <PieChart>
                        <Pie data={verdictPieData} dataKey="value" nameKey="name" innerRadius={45} outerRadius={65} paddingAngle={3}>
                          {verdictPieData.map((entry, i) => (
                            <Cell key={i} fill={entry.color} stroke="none" />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={{ background: "#111815", border: "1px solid #212B26", borderRadius: 6, fontSize: 12 }} />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="flex justify-center gap-3 mt-2 flex-wrap">
                      {verdictPieData.map((v) => (
                        <span key={v.name} className="flex items-center gap-1.5 text-xs text-ash-300">
                          <span className="h-2 w-2 rounded-full" style={{ backgroundColor: v.color }} />
                          {v.name} ({v.value})
                        </span>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Second row: scans by type + top indicators */}
            <div className="grid lg:grid-cols-3 gap-4">
              <div className="panel p-4">
                <p className="label-caps mb-3">Scans by type</p>
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart data={typeBarData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#212B26" vertical={false} />
                    <XAxis dataKey="name" stroke="#7C8985" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis stroke="#7C8985" fontSize={11} tickLine={false} axisLine={false} allowDecimals={false} />
                    <Tooltip contentStyle={{ background: "#111815", border: "1px solid #212B26", borderRadius: 6, fontSize: 12 }} />
                    <Bar dataKey="value" fill="#D9A441" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="panel p-4 lg:col-span-2">
                <p className="label-caps mb-3">Top threat indicators (last 200 scans)</p>
                {stats.top_threat_indicators.length === 0 ? (
                  <div className="h-[160px] flex items-center justify-center text-xs text-ash-400">No indicators yet</div>
                ) : (
                  <ul className="space-y-2.5">
                    {stats.top_threat_indicators.map((t, i) => (
                      <li key={i} className="flex items-center gap-3">
                        <span className="text-xs text-ash-400 truncate flex-1">{t.indicator}</span>
                        <span className="text-xs font-mono text-signal shrink-0">{t.count}×</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            {/* Recent scans */}
            <div className="panel p-4">
              <div className="flex items-center justify-between mb-3">
                <p className="label-caps">Recent scans</p>
                <Link to="/history" className="text-xs text-signal hover:underline">View all</Link>
              </div>
              {recent.length === 0 ? (
                <EmptyState title="No scans yet" description="Run your first scan from the sidebar to see activity here." />
              ) : (
                <div className="divide-y divide-ink-border">
                  {recent.map((item) => (
                    <div key={item.id} className="flex items-center gap-3 py-2.5">
                      <span className="text-[11px] uppercase tracking-wide text-ash-400 w-16 shrink-0">{item.scan_type}</span>
                      <span className="flex-1 min-w-0 truncate text-sm font-mono text-ash-200">{item.target}</span>
                      <VerdictBadge verdict={item.verdict} />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
