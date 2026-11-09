import { CheckCircle2, Info, Link2, Percent } from "lucide-react";
import RiskGauge from "./RiskGauge";
import VerdictBadge from "./VerdictBadge";

const FACTOR_COLORS = {
  safe: "#33C17E",
  suspicious: "#E8A93B",
  malicious: "#E15559",
};

function factorColor(weight) {
  if (weight >= 25) return FACTOR_COLORS.malicious;
  if (weight >= 12) return FACTOR_COLORS.suspicious;
  return FACTOR_COLORS.safe;
}

export default function ScanResultPanel({ result }) {
  if (!result) return null;
  const { verdict, risk_score, confidence, explanation = [], factors = [], details = {} } = result;
  const maxWeight = Math.max(...(factors.map((f) => f.weight) || [1]), 1);
  const embeddedUrls = details?.urls_found || [];

  return (
    <div className="panel p-5 md:p-6 space-y-6">
      {/* Header: gauge + verdict */}
      <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
        <RiskGauge score={risk_score} verdict={verdict} />
        <div className="flex-1 space-y-3 text-center sm:text-left">
          <div className="flex flex-col sm:flex-row sm:items-center gap-2">
            <VerdictBadge verdict={verdict} size="lg" />
            <span className="inline-flex items-center gap-1 text-xs text-ash-400 justify-center sm:justify-start">
              <Percent className="h-3 w-3" /> {confidence}% model confidence
            </span>
          </div>
          <p className="text-sm text-ash-200 break-all font-mono">{result.target}</p>
          <p className="text-xs text-ash-400">
            Scanned via {result.source === "heuristic+ml" ? "rule engine + ML model" : "rule engine"}
            {result.created_at ? ` · ${new Date(result.created_at).toLocaleString()}` : ""}
          </p>
        </div>
      </div>

      {/* Explanation */}
      <div>
        <p className="label-caps mb-2 flex items-center gap-1.5">
          <Info className="h-3.5 w-3.5" /> Why this result
        </p>
        <ul className="space-y-2">
          {explanation.map((reason, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-ash-200">
              <CheckCircle2 className="h-3.5 w-3.5 mt-0.5 text-signal shrink-0" />
              {reason}
            </li>
          ))}
        </ul>
      </div>

      {/* Factor weight breakdown */}
      {factors.length > 0 && (
        <div>
          <p className="label-caps mb-2">Risk factor breakdown</p>
          <div className="space-y-2">
            {factors
              .slice()
              .sort((a, b) => b.weight - a.weight)
              .map((f, i) => (
                <div key={i}>
                  <div className="flex items-center justify-between text-xs text-ash-300 mb-1">
                    <span className="truncate pr-2">{f.label}</span>
                    <span className="text-ash-400 shrink-0">+{f.weight}</span>
                  </div>
                  <div className="h-1.5 w-full rounded-full bg-ink-border overflow-hidden">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${(f.weight / maxWeight) * 100}%`,
                        backgroundColor: factorColor(f.weight),
                      }}
                    />
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Embedded URLs (message scans) */}
      {embeddedUrls.length > 0 && (
        <div>
          <p className="label-caps mb-2 flex items-center gap-1.5">
            <Link2 className="h-3.5 w-3.5" /> Links found in this message
          </p>
          <div className="space-y-2">
            {embeddedUrls.map((u, i) => (
              <div key={i} className="flex items-center justify-between gap-3 rounded-md border border-ink-border bg-ink-raised/50 px-3 py-2">
                <span className="text-xs font-mono text-ash-200 truncate">{u.url}</span>
                <span
                  className="text-xs font-medium shrink-0"
                  style={{ color: factorColor(u.risk_score >= 65 ? 30 : u.risk_score >= 30 ? 15 : 0) }}
                >
                  {Math.round(u.risk_score)}/100
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
