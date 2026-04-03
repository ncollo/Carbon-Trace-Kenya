import { api } from "../api/client";
import { useFetch } from "../hooks/useFetch";
import { Loading, ApiError } from "../components/Status";
import Card from "../components/Card";
import KpiCard from "../components/KpiCard";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from "recharts";

const tt = { contentStyle:{ background:"#0f1f36", border:"1px solid #1e3450", borderRadius:8, color:"#e2e8f0", fontSize:11, fontFamily:"'DM Sans',sans-serif" } };

export default function OverviewPage() {
  const kpis    = useFetch(api.kpis);
  const trend   = useFetch(api.quarterlyTrend);
  const scopes  = useFetch(api.scopeBreakdown);
  const fleet   = useFetch(api.fleetByClass);
  const cos     = useFetch(api.companies);

  const benchColors = (i, total) => {
    if (i === 0) return "#22c55e";
    if (i < total * 0.25) return "#4ade80";
    if (i < total * 0.75) return "#f59e0b";
    return "#ef4444";
  };

  if (kpis.error) return <ApiError error={kpis.error} onRetry={kpis.refetch} />;

  const k = kpis.data || {};

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.loading ? [1,2,3,4].map(i => <div key={i} className="rounded-2xl p-5 glass animate-pulse h-24" />) : <>
          <KpiCard label="Total Scope 1+3" value={k.total_tco2e?.toLocaleString()} unit="tCO₂e" delta={`Scope 1: ${k.scope1_tco2e?.toLocaleString()} t`} />
          <KpiCard label="Avg intensity" value={k.avg_intensity?.toFixed(2)} unit="tCO₂e/KSh M" delta={`${k.n_companies} companies`} accent="#22c55e" />
          <KpiCard label="Pending anomalies" value={k.pending_anomalies} unit="" delta={`${k.total_fuel_records?.toLocaleString()} total records`} deltaUp={k.pending_anomalies > 0} accent="#f59e0b" />
          <KpiCard label="Uncertainty ±" value={`${k.uncertainty_pct}%`} unit="95% CI" delta="Bayesian PyMC · 10K samples" accent="#8b5cf6" />
        </>}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2">
          <Card title="Quarterly emission trend" badge="From database · all companies">
            {trend.loading ? <Loading /> : trend.error ? <ApiError error={trend.error} /> : (
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={trend.data} margin={{ top:4, right:4, left:-24, bottom:0 }}>
                  <defs>
                    <linearGradient id="gGreen" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#22c55e" stopOpacity={0.25}/>
                      <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#0f2340" />
                  <XAxis dataKey="label" tick={{ fill:"#2d5a3d", fontSize:9 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill:"#2d5a3d", fontSize:9 }} axisLine={false} tickLine={false} />
                  <Tooltip {...tt} formatter={v => [`${v} tCO₂e`, "Emissions"]} />
                  <Area type="monotone" dataKey="value" stroke="#22c55e" strokeWidth={2} fill="url(#gGreen)" dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </Card>
        </div>

        <Card title="Emission by scope · live">
          {scopes.loading ? <Loading /> : scopes.error ? <ApiError error={scopes.error} /> : (
            <div className="space-y-3 mt-1">
              {(scopes.data || []).map(s => (
                <div key={s.name}>
                  <div className="flex justify-between text-xs mb-1">
                    <span style={{ color:"#64748b" }}>{s.name}</span>
                    <span className="font-semibold font-mono" style={{ color:s.color }}>{s.value?.toLocaleString()} t</span>
                  </div>
                  <div className="h-1.5 rounded-full overflow-hidden" style={{ background:"#0f2340" }}>
                    <div className="h-full rounded-full" style={{ width:`${s.pct}%`, background:s.color }} />
                  </div>
                  <div className="text-right text-xs mt-0.5" style={{ color:"#2d5a3d" }}>{s.pct}%</div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Card title="Fleet emission by vehicle class · from DB">
          {fleet.loading ? <Loading /> : fleet.error ? <ApiError error={fleet.error} /> : (
            <div className="space-y-3">
              {(fleet.data || []).map(v => (
                <div key={v.class} className="flex items-center gap-3">
                  <div className="w-28 shrink-0">
                    <div className="text-xs font-medium" style={{ color:"#94a3b8" }}>{v.name}</div>
                    <div className="text-xs" style={{ color:"#1e3450" }}>{v.units} units</div>
                  </div>
                  <div className="flex-1 h-1 rounded-full overflow-hidden" style={{ background:"#0f2340" }}>
                    <div className="h-full rounded-full" style={{ width:`${v.pct}%`, background:v.color }} />
                  </div>
                  <span className="text-xs font-mono font-semibold w-20 text-right" style={{ color:"#e2e8f0" }}>{v.value?.toLocaleString()} t</span>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card title="NSE companies · DB records" badge={`${(cos.data||[]).length} loaded`}>
          {cos.loading ? <Loading /> : cos.error ? <ApiError error={cos.error} /> : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs data-table">
                <thead>
                  <tr style={{ borderBottom:"1px solid #0f2340" }}>
                    {["Code","Sector","Total tCO₂e","Intensity","YoY %"].map(h => (
                      <th key={h} className="text-left py-1.5 px-2 font-semibold uppercase tracking-wider" style={{ color:"#2d5a3d", fontSize:9 }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(cos.data || []).slice(0,10).map((c, i) => (
                    <tr key={c.company_id} style={{ borderBottom:"1px solid #0a1628" }}>
                      <td className="py-2 px-2 font-mono" style={{ color:"#4ade80" }}>{c.nse_code}</td>
                      <td className="py-2 px-2" style={{ color:"#475569" }}>{c.sector}</td>
                      <td className="py-2 px-2 font-mono font-semibold" style={{ color:"#e2e8f0" }}>{c.total_tco2e?.toLocaleString()}</td>
                      <td className="py-2 px-2 font-mono" style={{ color:"#e2e8f0" }}>{c.intensity_tco2e_per_ksh_m?.toFixed(2)}</td>
                      <td className="py-2 px-2 font-mono" style={{ color: c.yoy_change_pct < 0 ? "#4ade80" : "#f87171" }}>
                        {c.yoy_change_pct > 0 ? "▲" : "▼"}{Math.abs(c.yoy_change_pct)?.toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
