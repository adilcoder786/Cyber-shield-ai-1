import { useState } from "react";
import { Search, Link2 } from "lucide-react";
import Topbar from "../components/Topbar";
import LoadingState from "../components/LoadingState";
import ErrorBanner from "../components/ErrorBanner";
import ScanResultPanel from "../components/ScanResultPanel";
import { scanUrl } from "../api/client";

const EXAMPLES = [
  { label: "Phishing example", value: "http://paypal-account-verify.tk/secure/login", tone: "malicious" },
  { label: "Shortened link", value: "http://bit.ly/3xJ9kLm?login=chase&id=88213aa9", tone: "suspicious" },
  { label: "Legitimate site", value: "https://www.python.org/downloads/", tone: "safe" },
];

export default function UrlScanner() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!url.trim()) {
      setError("Please enter a URL to scan.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await scanUrl(url.trim());
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col">
      <Topbar title="URL Scanner" subtitle="Check a website or link for phishing risk before you click." />
      <div className="flex-1 px-5 md:px-8 py-6 space-y-6 max-w-3xl w-full">
        <form onSubmit={handleSubmit} className="panel p-4 md:p-5 space-y-3">
          <label className="label-caps flex items-center gap-1.5">
            <Link2 className="h-3.5 w-3.5" /> URL or website address
          </label>
          <div className="flex flex-col sm:flex-row gap-2">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/login"
              className="flex-1 rounded-md border border-ink-border bg-ink-raised px-3.5 py-2.5 text-sm text-ash-50 placeholder:text-ash-600 focus:border-signal outline-none font-mono"
            />
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-md bg-signal px-5 py-2.5 text-sm font-medium text-ink hover:bg-signal-soft transition-colors disabled:opacity-60"
            >
              <Search className="h-4 w-4" />
              {loading ? "Scanning…" : "Scan URL"}
            </button>
          </div>
          <div className="flex flex-wrap gap-2 pt-1">
            <span className="text-xs text-ash-400 mr-1">Try:</span>
            {EXAMPLES.map((ex) => (
              <button
                type="button"
                key={ex.value}
                onClick={() => setUrl(ex.value)}
                className="text-xs rounded-full border border-ink-border px-2.5 py-1 text-ash-300 hover:border-signal/40 hover:text-signal transition-colors"
              >
                {ex.label}
              </button>
            ))}
          </div>
        </form>

        <ErrorBanner message={error} />
        {loading && <LoadingState message="Analyzing URL structure, domain, and threat intel…" />}
        {!loading && result && <ScanResultPanel result={result} />}
      </div>
    </div>
  );
}
