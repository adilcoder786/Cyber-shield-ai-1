export default function StatCard({ label, value, icon: Icon, accent = "text-signal", sub }) {
  return (
    <div className="panel p-4">
      <div className="flex items-start justify-between">
        <p className="label-caps">{label}</p>
        {Icon && <Icon className={`h-4 w-4 ${accent}`} strokeWidth={2} />}
      </div>
      <p className="font-display text-3xl font-semibold text-ash-50 mt-2">{value}</p>
      {sub && <p className="text-xs text-ash-400 mt-1">{sub}</p>}
    </div>
  );
}
