export default function Card({ title, subtitle, badge, badgeColor="default", actions, children }) {
  const chipClass =
    badgeColor === "green"  ? "chip chip-green"  :
    badgeColor === "amber"  ? "chip chip-amber"  :
    badgeColor === "red"    ? "chip chip-red"    :
    badgeColor === "blue"   ? "chip chip-blue"   :
    badgeColor === "purple" ? "chip chip-purple" :
    "chip";

  return (
    <section className="surface">
      {(title || badge) && (
        <header
          className="flex items-center justify-between"
          style={{ padding:"14px 20px", borderBottom:"1px solid var(--border)" }}
        >
          <div className="min-w-0">
            {title && (
              <h3 style={{ fontSize:13, fontWeight:600, color:"var(--text)", letterSpacing:"-0.005em", margin:0 }}>
                {title}
              </h3>
            )}
            {subtitle && (
              <p style={{ fontSize:11, marginTop:2, color:"var(--text-mute)", margin:"2px 0 0" }} className="truncate">
                {subtitle}
              </p>
            )}
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {actions}
            {badge && <span className={chipClass}>{badge}</span>}
          </div>
        </header>
      )}
      <div style={{ padding:20 }}>{children}</div>
    </section>
  );
}
