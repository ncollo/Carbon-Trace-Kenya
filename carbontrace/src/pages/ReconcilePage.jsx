import { useState } from "react";
import { api } from "../api/client";
import { useFetch } from "../hooks/useFetch";
import { Loading, ApiError } from "../components/Status";
import Card from "../components/Card";

export default function ReconcilePage() {
  const quality  = useFetch(api.quality);
  const flags    = useFetch(() => api.flags("pending"));
  const valLog   = useFetch(api.validationLog);
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
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label:"Records validated", value: q.clean_records?.toLocaleString() || "—", sub:`of ${q.total_records?.toLocaleString() || "—"}`, color:"#4ade80" },
          { label:"Pending flags",     value: q.pending_flags ?? "—", sub:"require attention", color: q.pending_flags > 0 ? "#f87171" : "#4ade80" },
          { label:"Emission at risk",  value: q.pending_impact_tco2e ?? "—", sub:"tCO₂e if unresolved", color:"#f59e0b" },
          { label:"Accuracy",          value: `${q.clean_pct ?? "—"}%`, sub:"post-reconciliation", color:"#4ade80" },
        ].map(k => (
          <div key={k.label} className="rounded-2xl p-4 glass glass-hover" style={{ border:"1px solid rgba(34,197,94,0.08)" }}>
            <div className="text-xs uppercase tracking-widest mb-1.5" style={{ color:"#2d5a3d", fontSize:9 }}>{k.label}</div>
            <div className="text-2xl font-semibold" style={{ color:k.color, fontFamily:"'DM Sans',sans-serif" }}>{k.value}</div>
            <div className="text-xs mt-1" style={{ color:"#475569" }}>{k.sub}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2">
          <Card title="Isolation Forest anomaly flags · live DB" badge={`${(flags.data||[]).length} pending`} badgeColor={(flags.data||[]).length > 0 ? "red" : "green"}>
            {flags.loading ? <Loading /> : flags.error ? <ApiError error={flags.error} onRetry={flags.refetch} /> : (flags.data||[]).length === 0 ? (
              <div className="text-center py-8">
                <div className="text-3xl mb-2 opacity-40">✓</div>
                <div className="text-sm" style={{ color:"#4ade80" }}>All anomalies resolved</div>
              </div>
            ) : (
              <div className="space-y-3">
                {(flags.data || []).map(flag => (
                  <div key={flag.anomaly_record_id} className="rounded-xl p-4 transition-all"
                    style={{ background:"rgba(239,68,68,0.05)", border:"1px solid rgba(239,68,68,0.2)" }}>
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                          <span className="text-xs font-bold font-mono" style={{ color:"#f87171" }}>{flag.anomaly_record_id}</span>
                          <span className="text-xs" style={{ color:"#475569" }}>· {flag.transaction_date}</span>
                          <span className="text-xs px-2 py-0.5 rounded" style={{ background:"rgba(239,68,68,0.1)", color:"#f87171", fontSize:10 }}>{flag.anomaly_type}</span>
                          <span className="text-xs px-2 py-0.5 rounded" style={{ background:"rgba(245,158,11,0.08)", color:"#fbbf24", fontSize:10 }}>Conf: {(flag.anomaly_confidence*100).toFixed(0)}%</span>
                        </div>
                        <p className="text-xs mb-1.5" style={{ color:"#94a3b8" }}>
                          Vehicle: <span className="font-mono">{flag.vehicle_id}</span> · Declared: <span className="font-mono">{flag.fuel_declared_l} L</span> · GPS: <span className="font-mono">{flag.gps_km_logged} km</span> · Expected: <span className="font-mono">{flag.expected_fuel_l} L</span>
                        </p>
                        <div className="flex gap-4">
                          <span className="text-xs" style={{ color:"#475569" }}>Impact: <span style={{ color:"#f87171", fontWeight:600 }}>+{flag.impact_tco2e} tCO₂e</span></span>
                          <span className="text-xs" style={{ color:"#475569" }}>Score: <span className="font-mono" style={{ color:"#fbbf24" }}>{flag.isolation_score}</span></span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleResolve(flag.anomaly_record_id)}
                        disabled={resolving[flag.anomaly_record_id]}
                        className="text-xs px-3 py-1.5 rounded-lg transition-all shrink-0 font-medium"
                        style={{ background:"rgba(34,197,94,0.1)", color:"#4ade80", border:"1px solid rgba(34,197,94,0.2)" }}>
                        {resolving[flag.anomaly_record_id] ? "Resolving…" : "Resolve"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        <Card title="Data quality · live">
          {quality.loading ? <Loading /> : (
            <div className="space-y-4">
              {[
                { label:"Clean records",    val: q.clean_records, total: q.total_records, color:"#22c55e" },
                { label:"Accuracy %",       val: q.clean_pct, total: 100, color:"#22c55e" },
                { label:"Emission at risk", val: Math.min(q.pending_impact_tco2e||0, 100), total: 100, color:"#f59e0b" },
              ].map(r => (
                <div key={r.label}>
                  <div className="flex justify-between text-xs mb-1">
                    <span style={{ color:"#64748b" }}>{r.label}</span>
                    <span style={{ color:r.color, fontWeight:600 }}>{r.val?.toLocaleString()}</span>
                  </div>
                  <div className="h-2 rounded-full overflow-hidden" style={{ background:"#0f2340" }}>
                    <div className="h-full rounded-full" style={{ width:`${Math.min(100,(r.val||0)/(r.total||1)*100)}%`, background:r.color }} />
                  </div>
                </div>
              ))}
              <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                {[
                  {v:q.clean_records, l:"Clean"},
                  {v:q.pending_flags, l:"Pending"},
                  {v:`${q.clean_pct?.toFixed(1)}%`, l:"Accuracy"},
                ].map(s => (
                  <div key={s.l} className="rounded-lg py-2" style={{ background:"#0a1628" }}>
                    <div className="font-bold text-sm" style={{ color:"#4ade80" }}>{s.v?.toLocaleString()}</div>
                    <div className="text-xs" style={{ color:"#475569" }}>{s.l}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>
      </div>

      <Card title="Validation log · real records from DB" badge="GPS × fuel × tank capacity">
        {valLog.loading ? <Loading /> : valLog.error ? <ApiError error={valLog.error} /> : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs data-table">
              <thead>
                <tr style={{ borderBottom:"1px solid #0f2340" }}>
                  {["ID","Vehicle","Date","Declared L","GPS km","Expected L","Delta L","Type","Status"].map(h => (
                    <th key={h} className="text-left py-2 px-2 font-semibold uppercase tracking-wider" style={{ color:"#2d5a3d", fontSize:9 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(valLog.data||[]).map((r,i) => (
                  <tr key={i} style={{ borderBottom:"1px solid #0a1628" }}>
                    <td className="py-2 px-2 font-mono" style={{ color:"#2d5a3d", fontSize:10 }}>{r.anomaly_record_id}</td>
                    <td className="py-2 px-2 font-mono" style={{ color:"#94a3b8", fontSize:10 }}>{r.vehicle_id}</td>
                    <td className="py-2 px-2" style={{ color:"#475569" }}>{r.transaction_date}</td>
                    <td className="py-2 px-2 font-mono" style={{ color:"#e2e8f0" }}>{r.fuel_declared_l}</td>
                    <td className="py-2 px-2 font-mono" style={{ color:"#e2e8f0" }}>{r.gps_km_logged}</td>
                    <td className="py-2 px-2 font-mono" style={{ color:"#e2e8f0" }}>{r.expected_fuel_l}</td>
                    <td className="py-2 px-2 font-mono font-semibold" style={{ color: r.delta_fuel_l > 5 ? "#f87171" : "#4ade80" }}>{r.delta_fuel_l?.toFixed(1)}</td>
                    <td className="py-2 px-2" style={{ color:"#64748b" }}>{r.anomaly_type}</td>
                    <td className="py-2 px-2">
                      <span className="px-1.5 py-0.5 rounded text-xs"
                        style={r.resolution_status==="resolved" ? { background:"rgba(34,197,94,0.1)", color:"#4ade80" }
                          : r.resolution_status==="escalated" ? { background:"rgba(239,68,68,0.1)", color:"#f87171" }
                          : { background:"rgba(245,158,11,0.1)", color:"#fbbf24" }}>
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
