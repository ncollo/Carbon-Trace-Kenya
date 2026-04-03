import { useApp } from "../context/AppContext";

const NAV = [
  { id:"overview",   icon:"◈", label:"Overview",          sub:"Dashboard" },
  { id:"ingestion",  icon:"⬆", label:"Data Ingestion",    sub:"AI extraction" },
  { id:"reconcile",  icon:"⚡", label:"Reconciliation",    sub:"Anomaly flags",  badge:true },
  { id:"calculator", icon:"⊕", label:"GHG Calculator",    sub:"Emission engine" },
  { id:"report",     icon:"◻", label:"Disclosure Report", sub:"PDF + XBRL" },
  { id:"epra",       icon:"⊞", label:"EPRA Analytics",    sub:"Sector + NDC" },
];

export default function Sidebar() {
  const { activePage, setActivePage, anomalyFlags } = useApp();
  return (
    <aside className="flex flex-col w-60 min-w-60 border-r" style={{ background:"#07111f", borderColor:"#0f2340" }}>
      {/* Logo */}
      <div className="px-5 pt-6 pb-5 border-b" style={{ borderColor:"#0f2340" }}>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background:"rgba(34,197,94,0.15)", border:"1px solid rgba(34,197,94,0.3)" }}>
            <span className="text-green-400 text-sm font-bold">C</span>
          </div>
          <span style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:700, fontSize:16, color:"#4ade80", letterSpacing:"-0.5px" }}>CarbonTrace</span>
        </div>
        <div className="text-xs" style={{ color:"#2d5a3d", letterSpacing:"2px", textTransform:"uppercase", fontSize:9 }}>Kenya · EPRA 2026 · EmitIQ</div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {NAV.map(item => {
          const isActive = activePage === item.id;
          const flagCount = item.badge ? anomalyFlags.length : 0;
          return (
            <button key={item.id} onClick={() => setActivePage(item.id)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all duration-200 group"
              style={{
                background: isActive ? "rgba(34,197,94,0.1)" : "transparent",
                border: isActive ? "1px solid rgba(34,197,94,0.2)" : "1px solid transparent",
              }}
            >
              <span className="text-sm w-4 text-center shrink-0 transition-transform duration-200 group-hover:scale-110"
                style={{ color: isActive ? "#4ade80" : "#2d5a3d" }}>
                {item.icon}
              </span>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-semibold leading-tight" style={{ color: isActive ? "#4ade80" : "#64748b" }}>
                  {item.label}
                </div>
                <div className="text-xs leading-tight mt-0.5" style={{ color: isActive ? "#22c55e60" : "#1e3450" }}>
                  {item.sub}
                </div>
              </div>
              {item.badge && flagCount > 0 && (
                <span className="text-xs px-1.5 py-0.5 rounded-full font-bold" style={{ background:"rgba(239,68,68,0.15)", color:"#f87171", border:"1px solid rgba(239,68,68,0.3)", fontSize:10 }}>
                  {flagCount}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Status + Company */}
      <div className="px-4 py-4 border-t space-y-3" style={{ borderColor:"#0f2340" }}>
        <div className="flex items-center gap-2 px-2 py-2 rounded-lg" style={{ background:"rgba(34,197,94,0.05)", border:"1px solid rgba(34,197,94,0.1)" }}>
          <div className="relative flex-shrink-0">
            <div className="w-1.5 h-1.5 rounded-full bg-green-400" />
            <div className="absolute inset-0 rounded-full bg-green-400 animate-ping opacity-40" />
          </div>
          <div>
            <div className="text-xs font-medium" style={{ color:"#4ade80" }}>Pipeline active</div>
            <div className="text-xs" style={{ color:"#1e3450", fontSize:10 }}>Module 3 — GHG engine</div>
          </div>
        </div>
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0"
            style={{ background:"rgba(34,197,94,0.1)", color:"#4ade80", border:"1px solid rgba(34,197,94,0.2)" }}>KP</div>
          <div>
            <div className="text-xs font-semibold" style={{ color:"#94a3b8" }}>Kenya Power Ltd</div>
            <div className="text-xs" style={{ color:"#1e3450" }}>ESG Officer · NSE Listed</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
