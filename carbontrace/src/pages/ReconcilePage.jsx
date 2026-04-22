import { useState } from "react";
import { api } from "../api/client";
import { useFetch } from "../hooks/useFetch";
import { Loading, ApiError } from "../components/Status";
import Card from "../components/Card";
import { Icon } from "../components/Icons";

export default function ReconcilePage() {
  const quality = useFetch(api.quality);
  const flags   = useFetch(() => api.flags("pending"));
  const valLog  = useFetch(api.validationLog);
  const [resolving, setResolving] = useState({});

  const handleResolve = async (id) => {
    setResolving(r => ({ ...r, [id]: true }));
    try {
      await api.resolveFlag(id);
      await flags.refetch();
      await quality.refetch();
    } catch(e) { console.error(e); }
    finally { setResolving(r => ({ ...r, [id]: false })); }
  };

  const q = quality.data || {};

  return (
    <div className="space-y-5">
      {/* KPI row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label:"Records validated", value: q.clean_records?.toLocaleString() || "—", sub:`of ${q.total_records?.toLocaleString() || "—"}` },
          { label:"Pending flags",     value: q.pending_flags ?? "—",                   sub:"require attention",    accent: q.pending_flags > 0 ? "var(--bad-text)" : "var(--ok-text)" },
          { label:"Emission at risk",  value: q.pending_impact_tco2e ?? "—",            sub:"tCO2e if unresolved",  accent:"var(--warn-text)" },
          { label:"Accuracy",          value: `${q.clean_pct ?? "—"}%`,                 sub:"post-reconciliation",  accent:"var(--ok-text)" },
        ].map(({ label, value, sub, accent = "var(--text)" }) => (
          <div key={label} className="surface surface-hover" style={{ padding:16 }}>
            <div style={{ fontSize:10, textTransform:"uppercase", letterSpacing:"0.08em", fontWeight:500, color:"var(--text-mute)", marginBottom:8 }}>
              {label}
            </div>
            <div style={{ fontSize:22, fontWeight:600, letterSpacing:"-0.015em", color:accent }}>{value}</div>
            <div style={{ fontSize:11, marginTop:4, color:"var(--text-dim)" }}>{sub}</div>
          </div>
        ))}
      </div>

      {/* Flags + Data quality */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2">
          <Card
            title="Isolation Forest anomaly flags"
            subtitle="Live from DB"
            badge={`${(flags.data||[]).length} pending`}
            badgeColor={(flags.data||[]).length > 0 ? "red" : "green"}
          >
            {flags.loading ? <Loading /> : flags.error ? <ApiError error={flags.error} onRetry={flags.refetch} /> :
              (flags.data||[]).length === 0 ? (
                <div className="text-center py-8">
                  <div className="flex items-center justify-center mx-auto mb-3" style={{
                    width:40, height:40, borderRadius:"50%",
                    background:"var(--ok-bg)", border:"1px solid var(--ok-border)", color:"var(--ok-text)",
                  }}>
                    <Icon.Check />
                  </div>
                  <div style={{ fontSize:14, color:"var(--text)" }}>All anomalies resolved</div>
                </div>
              ) : (
                <div className="space-y-3">
                  {(flags.data || []).map(flag => (
                    <div key={flag.anomaly_record_id} style={{ borderRadius:8, padding:16, background:"var(--bad-bg)", border:"1px solid var(--bad-border)" }}>
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap" style={{ marginBottom:8 }}>
                            <span className="font-mono font-semibold" style={{ fontSize:12, color:"var(--bad-text)" }}>
                              {flag.anomaly_record_id}
                            </span>
                            <span style={{ fontSize:11, color:"var(--text-mute)" }}>{flag.transaction_date}</span>
                            <span className="chip chip-red" style={{ fontSize:10 }}>{flag.anomaly_type}</span>
                            <span className="chip chip-amber" style={{ fontSize:10 }}>
                              Confidence {(flag.anomaly_confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                          <p style={{ fontSize:12, marginBottom:8, color:"var(--text-dim)" }}>
                            Vehicle <span className="font-mono" style={{ color:"var(--text)" }}>{flag.vehicle_id}</span>
                            {" · "}Declared <span className="font-mono" style={{ color:"var(--text)" }}>{flag.fuel_declared_l} L</span>
                            {" · "}GPS <span className="font-mono" style={{ color:"var(--text)" }}>{flag.gps_km_logged} km</span>
                            {" · "}Expected <span className="font-mono" style={{ color:"var(--text)" }}>{flag.expected_fuel_l} L</span>
                          </p>
                          <div className="flex gap-5" style={{ fontSize:11, color:"var(--text-mute)" }}>
                            <span>Impact <span className="font-mono font-medium" style={{ color:"var(--bad-text)" }}>+{flag.impact_tco2e} tCO2e</span></span>
                            <span>Score <span className="font-mono" style={{ color:"var(--warn-text)" }}>{flag.isolation_score}</span></span>
                          </div>
                        </div>
                        <button
                          onClick={() => handleResolve(flag.anomaly_record_id)}
                          disabled={resolving[flag.anomaly_record_id]}
                          style={{
                            fontSize:11, fontWeight:500, padding:"6px 12px", borderRadius:6, flexShrink:0,
                            background:"var(--surface-3)", color:"var(--text)", border:"1px solid var(--border-2)", cursor:"pointer",
                          }}
                        >
                          {resolving[flag.anomaly_record_id] ? "Resolving..." : "Resolve"}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )
            }
          </Card>
        </div>

        <Card title="Data quality" subtitle="Live">
          {quality.loading ? <Loading /> : (
            <div className="space-y-4">
              {[
                { label:"Clean records",    val: q.clean_records, total: q.total_records, color:"var(--accent)" },
                { label:"Accuracy",         val: q.clean_pct,     total: 100,             color:"var(--accent)" },
                { label:"Emission at risk", val: Math.min(q.pending_impact_tco2e||0, 100), total: 100, color:"var(--warn)" },
              ].map(r => (
                <div key={r.label}>
                  <div className="flex justify-between text-xs" style={{ marginBottom:6 }}>
                    <span style={{ color:"var(--text-dim)" }}>{r.label}</span>
                    <span className="font-mono font-medium" style={{ color:"var(--text)" }}>{r.val?.toLocaleString()}</span>
                  </div>
                  <div style={{ height:6, borderRadius:999, overflow:"hidden", background:"var(--track)" }}>
                    <div style={{ width:`${Math.min(100,(r.val||0)/(r.total||1)*100)}%`, height:"100%", background:r.color }} />
                  </div>
                </div>
              ))}
              <div className="grid grid-cols-3 gap-2" style={{ paddingTop:12 }}>
                {[
                  { v:q.clean_records, l:"Clean" },
                  { v:q.pending_flags, l:"Pending" },
                  { v:`${q.clean_pct?.toFixed(1)}%`, l:"Accuracy" },
                ].map(s => (
                  <div key={s.l} className="text-center" style={{ borderRadius:6, padding:"8px 4px", background:"var(--inset)", border:"1px solid var(--border)" }}>
                    <div className="font-mono font-semibold" style={{ fontSize:14, color:"var(--text)" }}>
                      {typeof s.v === "number" ? s.v?.toLocaleString() : s.v}
                    </div>
                    <div style={{ fontSize:11, color:"var(--text-mute)" }}>{s.l}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>
      </div>

      {/* Validation log */}
      <Card title="Validation log" subtitle="Real records from DB" badge="GPS x fuel x tank capacity">
        {valLog.loading ? <Loading /> : valLog.error ? <ApiError error={valLog.error} /> : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs data-table" style={{ borderCollapse:"collapse" }}>
              <thead>
                <tr style={{ borderBottom:"1px solid var(--border)" }}>
                  {["ID","Vehicle","Date","Declared L","GPS km","Expected L","Delta L","Type","Status"].map(h => (
                    <th key={h} className="text-left uppercase tracking-wider" style={{ padding:"8px 8px", fontSize:10, fontWeight:500, color:"var(--text-mute)" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(valLog.data||[]).map((r,i) => (
                  <tr key={i}>
                    <td className="font-mono" style={{ padding:"8px 8px", fontSize:10, color:"var(--text-mute)" }}>{r.anomaly_record_id}</td>
                    <td className="font-mono" style={{ padding:"8px 8px", fontSize:10, color:"var(--text-dim)" }}>{r.vehicle_id}</td>
                    <td style={{ padding:"8px 8px", color:"var(--text-dim)" }}>{r.transaction_date}</td>
                    <td className="font-mono" style={{ padding:"8px 8px", color:"var(--text)" }}>{r.fuel_declared_l}</td>
                    <td className="font-mono" style={{ padding:"8px 8px", color:"var(--text)" }}>{r.gps_km_logged}</td>
                    <td className="font-mono" style={{ padding:"8px 8px", color:"var(--text)" }}>{r.expected_fuel_l}</td>
                    <td className="font-mono font-semibold" style={{ padding:"8px 8px", color: r.delta_fuel_l > 5 ? "var(--bad-text)" : "var(--ok-text)" }}>
                      {r.delta_fuel_l?.toFixed(1)}
                    </td>
                    <td style={{ padding:"8px 8px", color:"var(--text-dim)" }}>{r.anomaly_type}</td>
                    <td style={{ padding:"8px 8px" }}>
                      <span className={
                        r.resolution_status === "resolved" ? "chip chip-green" :
                        r.resolution_status === "escalated" ? "chip chip-red" :
                        "chip chip-amber"
                      } style={{ fontSize:10 }}>
                        {r.resolution_status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
