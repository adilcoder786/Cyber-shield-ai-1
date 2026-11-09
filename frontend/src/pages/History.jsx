import { useEffect, useState } from "react";
import { Search, Trash2, ChevronLeft, ChevronRight, ListFilter, Inbox } from "lucide-react";
import Topbar from "../components/Topbar";
import VerdictBadge from "../components/VerdictBadge";
import EmptyState from "../components/EmptyState";
import ErrorBanner from "../components/ErrorBanner";
import { getHistory, deleteScan } from "../api/client";

const TYPE_LABEL = { url: "URL", message: "Message", file: "File" };
const PAGE_SIZE = 8;

export default function History() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [scanType, setScanType] = useState("");
  const [verdict, setVerdict] = useState("");
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const params = { page, page_size: PAGE_SIZE };
      if (scanType) params.scan_type = scanType;
      if (verdict) params.verdict = verdict;
      if (search) params.search = search;
      const data = await getHistory(params);
      setItems(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, scanType, verdict]);

  function handleSearchSubmit(e) {
    e.preventDefault();
    setPage(1);
    load();
  }

  async function handleDelete(id) {
    try {
      await deleteScan(id);
      setItems((prev) => prev.filter((i) => i.id !== id));
      setTotal((t) => t - 1);
    } catch (err) {
      setError(err.message);
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="flex-1 flex flex-col">
      <Topbar title="Scan History" subtitle={`${total} scans recorded`} />
      <div className="flex-1 px-5 md:px-8 py-6 space-y-4">
        <div className="panel p-4 flex flex-col md:flex-row gap-3">
          <form onSubmit={handleSearchSubmit} className="flex-1 flex gap-2">
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by URL, filename, or message text…"
              className="flex-1 rounded-md border border-ink-border bg-ink-raised px-3 py-2 text-sm text-ash-50 placeholder:text-ash-600 focus:border-signal outline-none"
            />
            <button type="submit" className="rounded-md border border-ink-border px-3 py-2 text-ash-300 hover:text-signal hover:border-signal/40">
              <Search className="h-4 w-4" />
            </button>
          </form>
          <div className="flex gap-2">
            <select
              value={scanType}
              onChange={(e) => { setScanType(e.target.value); setPage(1); }}
              className="rounded-md border border-ink-border bg-ink-raised px-3 py-2 text-sm text-ash-200 focus:border-signal outline-none"
            >
              <option value="">All types</option>
              <option value="url">URL</option>
              <option value="message">Message</option>
              <option value="file">File</option>
            </select>
            <select
              value={verdict}
              onChange={(e) => { setVerdict(e.target.value); setPage(1); }}
              className="rounded-md border border-ink-border bg-ink-raised px-3 py-2 text-sm text-ash-200 focus:border-signal outline-none"
            >
              <option value="">All verdicts</option>
              <option value="safe">Safe</option>
              <option value="suspicious">Suspicious</option>
              <option value="malicious">Malicious</option>
            </select>
          </div>
        </div>

        <ErrorBanner message={error} />

        {loading ? (
          <div className="panel py-14 text-center text-sm text-ash-400">Loading history…</div>
        ) : items.length === 0 ? (
          <EmptyState icon={Inbox} title="No scans found" description="Run a scan or adjust your filters to see results here." />
        ) : (
          <div className="panel divide-y divide-ink-border overflow-hidden">
            {items.map((item) => (
              <div key={item.id}>
                <button
                  onClick={() => setExpanded(expanded === item.id ? null : item.id)}
                  className="w-full flex items-center gap-3 px-4 py-3.5 text-left hover:bg-ink-raised/40 transition-colors"
                >
                  <span className="text-[11px] uppercase tracking-wide text-ash-400 w-16 shrink-0">
                    {TYPE_LABEL[item.scan_type]}
                  </span>
                  <span className="flex-1 min-w-0 truncate text-sm font-mono text-ash-200">{item.target}</span>
                  <span className="text-xs font-mono text-ash-400 shrink-0 hidden sm:inline">
                    {Math.round(item.risk_score)}/100
                  </span>
                  <VerdictBadge verdict={item.verdict} />
                  <span className="text-xs text-ash-600 shrink-0 hidden md:inline">
                    {item.created_at ? new Date(item.created_at).toLocaleDateString() : ""}
                  </span>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }}
                    className="shrink-0 text-ash-600 hover:text-verdict-malicious transition-colors p-1"
                    aria-label="Delete scan"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </button>
                {expanded === item.id && (
                  <div className="px-4 pb-4 pl-[4.5rem]">
                    <ul className="space-y-1.5">
                      {item.explanation.map((reason, i) => (
                        <li key={i} className="text-xs text-ash-300 flex gap-2">
                          <span className="text-signal">•</span>
                          {reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {!loading && items.length > 0 && (
          <div className="flex items-center justify-between text-sm text-ash-400">
            <span className="flex items-center gap-1.5">
              <ListFilter className="h-3.5 w-3.5" /> Page {page} of {totalPages}
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="rounded-md border border-ink-border p-1.5 disabled:opacity-40 hover:border-signal/40"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="rounded-md border border-ink-border p-1.5 disabled:opacity-40 hover:border-signal/40"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
