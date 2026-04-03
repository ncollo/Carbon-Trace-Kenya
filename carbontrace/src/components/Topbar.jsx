export default function Topbar({ title, sub }) {
  return (
    <header className="flex items-center justify-between px-6 py-3 border-b sticky top-0 z-20"
      style={{ background:"rgba(6,14,26,0.95)", borderColor:"#0f2340", backdropFilter:"blur(12px)" }}>
      <div>
        <h1 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:600, fontSize:17, color:"#e2e8f0", lineHeight:1.2 }}>{title}</h1>
        <p className="text-xs mt-0.5" style={{ color:"#2d5a3d" }}>{sub}</p>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg" style={{ background:"rgba(34,197,94,0.08)", border:"1px solid rgba(34,197,94,0.15)" }}>
          <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs font-medium" style={{ color:"#4ade80" }}>NSE-Ready</span>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg" style={{ background:"rgba(15,31,54,0.8)", border:"1px solid #0f2340" }}>
          <span className="text-xs" style={{ color:"#475569" }}>FY 2025</span>
          <span className="text-xs font-mono" style={{ color:"#22c55e" }}>4,821 tCO₂e</span>
        </div>
      </div>
    </header>
  );
}
