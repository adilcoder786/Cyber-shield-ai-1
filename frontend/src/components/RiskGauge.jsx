const VERDICT_COLORS = {
  safe: "#33C17E",
  suspicious: "#E8A93B",
  malicious: "#E15559",
};

export default function RiskGauge({ score = 0, verdict = "safe", size = 168 }) {
  const stroke = 12;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, score));
  const offset = circumference - (clamped / 100) * circumference;
  const color = VERDICT_COLORS[verdict] || VERDICT_COLORS.safe;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#212B26"
          strokeWidth={stroke}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.8s ease-out, stroke 0.4s ease" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-4xl font-semibold text-ash-50">{Math.round(clamped)}</span>
        <span className="text-[11px] text-ash-400 -mt-1">out of 100</span>
      </div>
    </div>
  );
}
