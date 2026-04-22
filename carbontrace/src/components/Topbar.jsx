import { Icon } from "./Icons";

export default function Topbar({ title, sub, theme, onToggleTheme }) {
  return (
    <header
      className="flex items-center justify-between sticky top-0"
      style={{
        padding:"14px 20px",
        background:"var(--topbar-bg)",
        borderBottom:"1px solid var(--border)",
        backdropFilter:"blur(12px)",
        zIndex:20,
      }}
    >
      <div>
        <h1 style={{ fontWeight:600, fontSize:15, color:"var(--text)", lineHeight:1.25, letterSpacing:"-0.01em", margin:0 }}>
          {title}
        </h1>
        <p style={{ fontSize:11, marginTop:2, color:"var(--text-mute)", margin:"2px 0 0" }}>{sub}</p>
      </div>
      <div className="flex items-center gap-2">
        <span className="chip">
          <Icon.Search style={{ width:12, height:12 }} />
          <span style={{ color:"var(--text-mute)" }}>Search</span>
        </span>
        <span className="chip chip-green">
          <span className="dot" style={{ background:"var(--accent)" }} />
          NSE-ready
        </span>
        <span className="chip">
          <span style={{ color:"var(--text-mute)" }}>FY 2025</span>
          <span className="font-mono" style={{ color:"var(--text)" }}>4,821 tCO2e</span>
        </span>
        <button className="theme-btn" onClick={onToggleTheme} aria-label="Toggle theme">
          {theme === "dark" ? <Icon.Sun /> : <Icon.Moon />}
          <span>{theme === "dark" ? "Light" : "Dark"}</span>
        </button>
      </div>
    </header>
  );
}
