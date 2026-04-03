export default function Card({ title, badge, badgeColor="green", children, className="" }) {
  const badgeStyles = {
    green:  { bg:"rgba(34,197,94,0.1)",   color:"#4ade80",  border:"rgba(34,197,94,0.2)" },
    amber:  { bg:"rgba(245,158,11,0.1)",  color:"#fbbf24",  border:"rgba(245,158,11,0.2)" },
    red:    { bg:"rgba(239,68,68,0.1)",   color:"#f87171",  border:"rgba(239,68,68,0.2)" },
    blue:   { bg:"rgba(59,130,246,0.1)",  color:"#60a5fa",  border:"rgba(59,130,246,0.2)" },
    purple: { bg:"rgba(139,92,246,0.1)",  color:"#a78bfa",  border:"rgba(139,92,246,0.2)" },
  };
  const bc = badgeStyles[badgeColor] || badgeStyles.green;
  return (
    <div className={`rounded-2xl p-5 glass glass-hover ${className}`} style={{ border:"1px solid rgba(34,197,94,0.08)" }}>
      {title && (
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold" style={{ color:"#e2e8f0" }}>{title}</h3>
          {badge && (
            <span className="text-xs px-2 py-0.5 rounded-md font-medium"
              style={{ background:bc.bg, color:bc.color, border:`1px solid ${bc.border}` }}>
              {badge}
            </span>
          )}
        </div>
      )}
      {children}
    </div>
  );
}
