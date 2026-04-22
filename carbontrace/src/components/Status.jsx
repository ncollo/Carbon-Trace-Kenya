import { Icon } from "./Icons";

export function Loading({ label = "Loading..." }) {
  return (
    <div className="flex items-center gap-2 py-8 justify-center">
      <div
        className="animate-spin"
        style={{
          width:16, height:16, borderRadius:"50%",
          border:"2px solid var(--border)", borderTopColor:"var(--accent)",
        }}
      />
      <span style={{ fontSize:12, color:"var(--text-mute)" }}>{label}</span>
    </div>
  );
}

export function ApiError({ error, onRetry }) {
  return (
    <div
      className="flex items-center justify-between"
      style={{
        borderRadius:8, padding:16,
        background:"var(--bad-bg)", border:"1px solid var(--bad-border)",
      }}
    >
      <div>
        <div style={{ fontSize:12, fontWeight:600, color:"var(--bad-text)" }}>Backend unreachable</div>
        <div style={{ fontSize:11, marginTop:2, color:"var(--text-dim)" }}>
          {error} — is the backend running on port 8000?
        </div>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-1 shrink-0"
          style={{
            fontSize:12, padding:"6px 12px", borderRadius:6, marginLeft:16,
            background:"var(--bad-bg)", color:"var(--bad-text)", border:"1px solid var(--bad-border)",
            cursor:"pointer",
          }}
        >
          <Icon.Refresh style={{ width:12, height:12 }} />
          Retry
        </button>
      )}
    </div>
  );
}
