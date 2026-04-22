import { useApp } from "../context/AppContext";
import { Icon, BrandMark } from "./Icons";

const NAV = [
  { id:"overview",   Ico:Icon.Overview,   label:"Overview",          sub:"Dashboard" },
  { id:"ingestion",  Ico:Icon.Upload,     label:"Data Ingestion",    sub:"AI extraction" },
  { id:"reconcile",  Ico:Icon.Reconcile,  label:"Reconciliation",    sub:"Anomaly flags", badge:true },
  { id:"calculator", Ico:Icon.Calculator, label:"GHG Calculator",    sub:"Emission engine" },
  { id:"report",     Ico:Icon.Document,   label:"Disclosure Report", sub:"PDF + XBRL" },
  { id:"epra",       Ico:Icon.Analytics,  label:"EPRA Analytics",    sub:"Sector + NDC" },
];

export default function Sidebar() {
  const { activePage, setActivePage, anomalyFlags } = useApp();

  return (
    <aside className="flex flex-col" style={{ width:256, minWidth:256, background:"var(--sidebar-bg)", borderRight:"1px solid var(--border)" }}>
      {/* Logo */}
      <div className="px-5 pt-5 pb-4" style={{ borderBottom:"1px solid var(--border)" }}>
        <div className="flex items-center gap-2 mb-1">
          <BrandMark size={26} />
          <div>
            <div style={{ fontWeight:600, fontSize:14, color:"var(--text)", letterSpacing:"-0.01em" }}>CarbonTrace</div>
            <div style={{ fontSize:10, fontWeight:500, textTransform:"uppercase", letterSpacing:"0.08em", color:"var(--text-mute)" }}>
              Kenya · EPRA 2026
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto" style={{ display:"flex", flexDirection:"column", gap:2 }}>
        <div style={{ fontSize:10, fontWeight:500, textTransform:"uppercase", letterSpacing:"0.08em", color:"var(--text-faint)", padding:"0 12px 8px" }}>
          Workspace
        </div>
        {NAV.map(({ id, Ico, label, sub, badge }) => {
          const isActive = activePage === id;
          const flagCount = badge ? anomalyFlags.length : 0;
          return (
            <button
              key={id}
              onClick={() => setActivePage(id)}
              className="w-full flex items-center gap-3 text-left"
              style={{
                padding:"8px 12px",
                borderRadius:6,
                border:"none",
                cursor:"pointer",
                background: isActive ? "var(--surface-3)" : "transparent",
                color: isActive ? "var(--text)" : "var(--text-dim)",
                transition:"background 0.15s",
              }}
            >
              <span style={{ color: isActive ? "var(--accent)" : "var(--text-mute)", flexShrink:0 }}>
                <Ico />
              </span>
              <div className="flex-1 min-w-0">
                <div style={{ fontSize:12, fontWeight:500, lineHeight:1.25 }}>{label}</div>
                <div style={{ fontSize:11, lineHeight:1.25, marginTop:2, color:"var(--text-faint)" }}>{sub}</div>
              </div>
              {badge && flagCount > 0 && (
                <span className="font-mono" style={{
                  fontSize:10, fontWeight:600, padding:"2px 6px", borderRadius:4,
                  background:"var(--bad-bg)", color:"var(--bad-text)", border:"1px solid var(--bad-border)", flexShrink:0,
                }}>
                  {flagCount}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Status + User */}
      <div className="px-4 py-4" style={{ borderTop:"1px solid var(--border)", display:"flex", flexDirection:"column", gap:12 }}>
        <div className="flex items-center gap-2" style={{
          padding:"8px 12px", borderRadius:6,
          background:"var(--inset)", border:"1px solid var(--border)",
        }}>
          <span className="dot pulse-dot" style={{ background:"var(--accent)", flexShrink:0 }} />
          <div className="flex-1 min-w-0">
            <div style={{ fontSize:12, fontWeight:500, color:"var(--text)" }}>Pipeline active</div>
            <div style={{ fontSize:11, color:"var(--text-mute)" }}>Module 3 — GHG engine</div>
          </div>
        </div>
        <div className="flex items-center gap-2" style={{ padding:"0 4px" }}>
          <div className="flex items-center justify-center shrink-0" style={{
            width:32, height:32, borderRadius:6, fontSize:11, fontWeight:600,
            background:"var(--surface-3)", color:"var(--text)", border:"1px solid var(--border)",
          }}>KP</div>
          <div className="min-w-0">
            <div style={{ fontSize:12, fontWeight:500, color:"var(--text)" }} className="truncate">Kenya Power Ltd</div>
            <div style={{ fontSize:11, color:"var(--text-mute)" }}>ESG officer · NSE listed</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
