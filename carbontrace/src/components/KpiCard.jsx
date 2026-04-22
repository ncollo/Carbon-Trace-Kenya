import { Icon } from "./Icons";

export default function KpiCard({ label, value, unit, delta, deltaUp, accent = "var(--accent)" }) {
  const deltaColor = delta
    ? (deltaUp ? "var(--bad-text)" : "var(--ok-text)")
    : "var(--text-mute)";

  return (
    <div className="surface surface-hover" style={{ padding:16 }}>
      <div className="flex items-center justify-between" style={{ marginBottom:12 }}>
        <p style={{
          fontSize:10, textTransform:"uppercase", letterSpacing:"0.08em",
          fontWeight:500, color:"var(--text-mute)", margin:0,
        }}>
          {label}
        </p>
        <span className="dot" style={{ background:accent, opacity:0.7 }} />
      </div>
      <div className="flex items-baseline gap-1" style={{ marginBottom: delta ? 6 : 0 }}>
        <span style={{ fontWeight:600, fontSize:22, color:"var(--text)", letterSpacing:"-0.015em" }}>
          {value ?? "—"}
        </span>
        {unit && <span style={{ fontSize:11, color:"var(--text-mute)" }}>{unit}</span>}
      </div>
      {delta && (
        <p className="flex items-center gap-1" style={{ fontSize:11, color:deltaColor, margin:0 }}>
          {deltaUp ? <Icon.ArrowUp style={{ width:12, height:12 }} /> : <Icon.ArrowDown style={{ width:12, height:12 }} />}
          <span>{delta}</span>
        </p>
      )}
    </div>
  );
}
