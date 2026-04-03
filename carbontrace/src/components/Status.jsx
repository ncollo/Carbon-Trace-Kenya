export function Loading({ label = "Loading…" }) {
  return (
    <div className="flex items-center gap-2 py-8 justify-center">
      <div className="w-4 h-4 rounded-full border-2 border-transparent border-t-green-500 animate-spin" />
      <span className="text-xs" style={{ color: "#2d5a3d" }}>{label}</span>
    </div>
  );
}

export function ApiError({ error, onRetry }) {
  return (
    <div className="rounded-xl p-4 flex items-center justify-between"
      style={{ background: "rgba(239,68,68,0.06)", border: "1px solid rgba(239,68,68,0.2)" }}>
      <div>
        <div className="text-xs font-semibold" style={{ color: "#f87171" }}>Backend unreachable</div>
        <div className="text-xs mt-0.5" style={{ color: "#475569" }}>
          {error} — is the backend running on port 8000?
        </div>
      </div>
      {onRetry && (
        <button onClick={onRetry}
          className="text-xs px-3 py-1.5 rounded-lg ml-4 shrink-0"
          style={{ background: "rgba(239,68,68,0.1)", color: "#f87171", border: "1px solid rgba(239,68,68,0.2)" }}>
          Retry
        </button>
      )}
    </div>
  );
}
