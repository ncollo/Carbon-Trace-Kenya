export default function KpiCard({ label, value, unit, delta, deltaUp, accent="#4ade80" }) {
  return (
    <div className="rounded-2xl p-5 glass glass-hover relative overflow-hidden" style={{ border:"1px solid rgba(34,197,94,0.08)" }}>
      <div className="absolute inset-0 opacity-5" style={{ background:`radial-gradient(circle at top right, ${accent}, transparent 70%)` }} />
      <p className="text-xs uppercase tracking-widest mb-2" style={{ color:"#2d5a3d", fontSize:9 }}>{label}</p>
      <div className="flex items-baseline gap-1.5">
        <span className="font-semibold text-2xl" style={{ fontFamily:"'DM Sans',sans-serif", color:"#e2e8f0" }}>{value}</span>
        {unit && <span className="text-xs" style={{ color:"#475569" }}>{unit}</span>}
      </div>
      {delta && (
        <p className="text-xs mt-1.5" style={{ color: deltaUp ? "#f87171" : "#4ade80" }}>
          {delta}
        </p>
      )}
    </div>
  );
}
