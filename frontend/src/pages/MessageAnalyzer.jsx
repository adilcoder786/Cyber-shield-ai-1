import { useState } from "react";
import { ScanSearch, MessageSquareWarning } from "lucide-react";
import Topbar from "../components/Topbar";
import LoadingState from "../components/LoadingState";
import ErrorBanner from "../components/ErrorBanner";
import ScanResultPanel from "../components/ScanResultPanel";
import { scanMessage } from "../api/client";

const CHANNELS = ["email", "sms", "whatsapp", "other"];

const EXAMPLES = [
  {
    label: "Fake bank alert",
    channel: "sms",
    content: "Your bank account has been locked due to suspicious activity. Please confirm your password and OTP to unlock it right away.",
  },
  {
    label: "Prize scam",
    channel: "whatsapp",
    content: "Congratulations! You have won a $1000 Amazon gift card. Claim your prize now before it expires, click the link and enter your card details.",
  },
  {
    label: "Legitimate email",
    channel: "email",
    content: "Hi team, quick reminder that our sprint planning meeting is scheduled for 10am tomorrow in the main conference room.",
  },
];

export default function MessageAnalyzer() {
  const [content, setContent] = useState("");
  const [channel, setChannel] = useState("email");
  const [sender, setSender] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!content.trim()) {
      setError("Please paste the message content to analyze.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await scanMessage(content.trim(), channel, sender.trim());
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col">
      <Topbar title="Message Analyzer" subtitle="Paste an email, SMS, or chat message to check for phishing language." />
      <div className="flex-1 px-5 md:px-8 py-6 space-y-6 max-w-3xl w-full">
        <form onSubmit={handleSubmit} className="panel p-4 md:p-5 space-y-3">
          <label className="label-caps flex items-center gap-1.5">
            <MessageSquareWarning className="h-3.5 w-3.5" /> Message content
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={6}
            placeholder="Paste the full email or message text here…"
            className="w-full rounded-md border border-ink-border bg-ink-raised px-3.5 py-3 text-sm text-ash-50 placeholder:text-ash-600 focus:border-signal outline-none resize-y"
          />

          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <label className="label-caps block mb-1.5">Channel</label>
              <select
                value={channel}
                onChange={(e) => setChannel(e.target.value)}
                className="w-full rounded-md border border-ink-border bg-ink-raised px-3 py-2.5 text-sm text-ash-50 focus:border-signal outline-none capitalize"
              >
                {CHANNELS.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <label className="label-caps block mb-1.5">Sender (optional)</label>
              <input
                type="text"
                value={sender}
                onChange={(e) => setSender(e.target.value)}
                placeholder="sender@example.com"
                className="w-full rounded-md border border-ink-border bg-ink-raised px-3 py-2.5 text-sm text-ash-50 placeholder:text-ash-600 focus:border-signal outline-none font-mono"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 rounded-md bg-signal px-5 py-2.5 text-sm font-medium text-ink hover:bg-signal-soft transition-colors disabled:opacity-60"
          >
            <ScanSearch className="h-4 w-4" />
            {loading ? "Analyzing…" : "Analyze Message"}
          </button>

          <div className="flex flex-wrap gap-2 pt-1">
            <span className="text-xs text-ash-400 mr-1">Try:</span>
            {EXAMPLES.map((ex) => (
              <button
                type="button"
                key={ex.label}
                onClick={() => {
                  setContent(ex.content);
                  setChannel(ex.channel);
                }}
                className="text-xs rounded-full border border-ink-border px-2.5 py-1 text-ash-300 hover:border-signal/40 hover:text-signal transition-colors"
              >
                {ex.label}
              </button>
            ))}
          </div>
        </form>

        <ErrorBanner message={error} />
        {loading && <LoadingState message="Scanning message language and embedded links…" />}
        {!loading && result && <ScanResultPanel result={result} />}
      </div>
    </div>
  );
}
