import { api } from "../api/client";
import { useFetch } from "../hooks/useFetch";
import { useTooltipStyle } from "../hooks/useTooltipStyle";
import { Loading, ApiError } from "../components/Status";
import Card from "../components/Card";
import KpiCard from "../components/KpiCard";
import { Icon } from "../components/Icons";
import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from "recharts";

export default function OverviewPage() {
  const tt      = useTooltipStyle();
  const kpis    = useFetch(api.kpis);
  const trend   = useFetch(api.quarterlyTrend);
  const scopes  = useFetch(api.scopeBreakdown);
  const fleet   = useFetch(api.fleetByClass);
  const cos     = useFetch(api.companies);

  if (kpis.error) return <ApiError error={kpis.error} onRetry={kpis.refetch} />;
  const k = kpis.data || {};

  return (
    <div className="space-y-5">
      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.loading
          ? [1,2,3,4].map(i => (
              <div key={i} className="surface animate-pulse" style={{ height:96 }} />
            ))
          : <>
              <KpiCard label="Total Scope 1+3"     value={k.total_tco2e?.toLocaleString()}   unit="tCO2e"       delta={`Scope 1: ${k.scope1_tco2e?.toLocaleString()} t`} />
              <KpiCard label="Avg intensity"        value={k.avg_intensity?.toFixed(2)}        unit="tCO2e/KSh M" delta={`${k.n_companies} companies`} />
              <KpiCard label="Pending anomalies"    value={k.pending_anomalies}                unit="flags"       delta={`${k.total_fuel_records?.toLocaleString()} records`} deltaUp={k.pending_anomalies > 0} accent="var(--warn)" />
              <KpiCard label="Uncertainty"          value={`±${k.uncertainty_pct}%`}           unit="95% CI"      delta="Bayesian PyMC · 10K samples" accent="var(--info)" />
            </>
        }
      </div>

      {/* Trend + Scope breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2">
          <Card title="Quarterly emission trend" subtitle="All companies · rolling 12 quarters" badge="From database">
            {trend.loading ? <Loading /> : trend.error ? <ApiError error={trend.error} /> : (
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={trend.data} margin={{ top:8, right:8, left:-20, bottom:0 }}>
                  <defs>
                    <linearGradient id="gGreen" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="var(--accent)" stopOpacity={0.22} />
                      <stop offset="95%" stopColor="var(--accent)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" vertical={false} />
                  <XAxis dataKey="label" tick={{ fill:"var(--text-mute)", fontSize:10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill:"var(--text-mute)", fontSize:10 }} axisLine={false} tickLine={false} />
                  <Tooltip {...tt} formatter={v => [`${v} tCO2e`, "Emissions"]} />
                  <Area type="monotone" dataKey="value" stroke="var(--accent)" strokeWidth={1.75} fill="url(#gGreen)" dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </Card>
        </div>

        <Card title="Emission by scope" subtitle="Live">
          {scopes.loading ? <Loading /> : scopes.error ? <ApiError error={scopes.error} /> : (
            <div className="space-y-4">
              {(scopes.data || []).map(s => (
                <div key={s.name}>
                  <div className="flex justify-between text-xs" style={{ marginBottom:6 }}>
                    <span style={{ color:"var(--text-dim)" }}>{s.name}</span>
                    <span className="font-mono font-medium" style={{ color:"var(--text)" }}>
                      {s.value?.toLocaleString()} t
                    </span>
                  </div>
                  <div style={{ height:4, borderRadius:999, overflow:"hidden", background:"var(--track)" }}>
                    <div style={{ width:`${s.pct}%`, height:"100%", background:s.color }} />
                  </div>
                  <div className="text-right font-mono" style={{ fontSize:10, marginTop:4, color:"var(--text-mute)" }}>
                    {s.pct}%
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Fleet + Companies */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Card title="Fleet emission by vehicle class" subtitle="Aggregated from DB">
          {fleet.loading ? <Loading /> : fleet.error ? <ApiError error={fleet.error} /> : (
            <div className="space-y-3">
              {(fleet.data || []).map(v => (
                <div key={v.class} className="flex items-center gap-3">
                  <div style={{ width:128, flexShrink:0 }}>
                    <div style={{ fontSize:12, fontWeight:500, color:"var(--text)" }}>{v.name}</div>
                    <div style={{ fontSize:11, color:"var(--text-mute)" }}>{v.units} units</div>
                  </div>
                  <div className="flex-1" style={{ height:4, borderRadius:999, overflow:"hidden", background:"var(--track)" }}>
                    <div style={{ width:`${v.pct}%`, height:"100%", background:v.color }} />
                  </div>
                  <span className="font-mono font-medium" style={{ fontSize:12, color:"var(--text)", width:80, textAlign:"right" }}>
                    {v.value?.toLocaleString()} t
                  </span>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card title="NSE companies" subtitle="Database records" badge={`${(cos.data||[]).length} loaded`}>
          {cos.loading ? <Loading /> : cos.error ? <ApiError error={cos.error} /> : (
            <div className="overflow-x-auto" style={{ margin:"0 -20px" }}>
              <table className="w-full text-xs data-table" style={{ borderCollapse:"collapse" }}>
                <thead>
                  <tr style={{ borderBottom:"1px solid var(--border)" }}>
                    {["Code","Sector","tCO2e","Intensity","YoY"].map(h => (
                      <th key={h} className="text-left uppercase tracking-wider" style={{ padding:"8px 12px", fontSize:10, fontWeight:500, color:"var(--text-mute)" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(cos.data || []).slice(0,10).map(c => (
                    <tr key={c.company_id}>
                      <td className="font-mono font-medium" style={{ padding:"10px 12px", color:"var(--text)" }}>{c.nse_code}</td>
                      <td style={{ padding:"10px 12px", color:"var(--text-dim)" }}>{c.sector}</td>
                      <td className="font-mono" style={{ padding:"10px 12px", color:"var(--text)" }}>{c.total_tco2e?.toLocaleString()}</td>
                      <td className="font-mono" style={{ padding:"10px 12px", color:"var(--text-dim)" }}>{c.intensity_tco2e_per_ksh_m?.toFixed(2)}</td>
                      <td className="font-mono" style={{ padding:"10px 12px", color: c.yoy_change_pct < 0 ? "var(--ok-text)" : "var(--bad-text)" }}>
                        <span className="flex items-center gap-1">
                          {c.yoy_change_pct > 0
                            ? <Icon.ArrowUp style={{ width:12, height:12 }} />
                            : <Icon.ArrowDown style={{ width:12, height:12 }} />
                          }
                          {Math.abs(c.yoy_change_pct)?.toFixed(1)}%
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
    </div>
  );
}
