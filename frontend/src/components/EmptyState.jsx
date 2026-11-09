export default function EmptyState({ icon: Icon, title, description }) {
  return (
    <div className="panel flex flex-col items-center justify-center gap-2 py-14 text-center px-6">
      {Icon && <Icon className="h-8 w-8 text-ash-600 mb-1" strokeWidth={1.5} />}
      <p className="text-sm font-medium text-ash-200">{title}</p>
      {description && <p className="text-xs text-ash-400 max-w-xs">{description}</p>}
    </div>
  );
}
