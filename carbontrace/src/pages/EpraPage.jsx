import { useState, useCallback } from "react";
import { api } from "../api/client";
import { useFetch } from "../hooks/useFetch";
import { Loading, ApiError } from "../components/Status";
import Card from "../components/Card";
import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, ReferenceLine,
} from "recharts";

const tt = {
  contentStyle: {
    background: "#0f1f36", border: "1px solid #1e3450",
    borderRadius: 8, color: "#e2e8f0", fontSize: 11,
    fontFamily: "'DM Sans',sans-serif",
  },
};

export default function EpraPage() {
  const kpis     = useFetch(api.epraKpis);
  const ndc      = useFetch(api.ndcTrajectory);
  const sectors  = useFetch(api.sectorBreakdown);
  const league   = useFetch(api.leagueTable);
  const county   = useFetch(api.countyDist);

  const [ev, setEv]     = useState(30);
  const [fe, setFe]     = useState(15);
  const [rw, setRw]     = useState(25);
  const [simResult, setSimResult] = useState(null);
  const [simRunning, setSimRunning] = useState(false);

  const k = kpis.data || {};

  const runSim = useCallback(async () => {
    setSimRunning(true);
    try {
      const baseline = (k.sector_total_tco2e || 218000);
      const result = await api.simulate({ ev_pct: ev, fe_pct: fe, rw_pct: rw, baseline });
      setSimResult(result);
    } catch (e) {
      console.error(e);
    } finally {
      setSimRunning(false);
    }
  }, [ev, fe, rw, k.sector_total_tco2e]);

  const sr = simResult || {};

  return (
    <div className="space-y-5">

      {/* Federated notice */}
      <div className="rounded-2xl px-5 py-3 flex items-center gap-3"
        style={{ background: "rgba(59,130,246,0.06)", border: "1px solid rgba(59,130,246,0.2)" }}>
        <span style={{ fontSize: 16, flexShrink: 0 }}>🔒</span>
        <p className="text-xs" style={{ color: "#60a5fa" }}>
          <span className="font-semibold">Federated model active.</span>{" "}
          All sector data aggregated from SQLite DB seeded from {(sectors.data || []).length} sector CSV records.
          PySyft federated learning — no raw company data shared in aggregates.
        </p>
      </div>

      {/* EPRA KPIs from DB */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.loading ? [1,2,3,4].map(i => (
          <div key={i} className="rounded-2xl p-5 glass animate-pulse h-24" />
        )) : kpis.error ? <ApiError error={kpis.error} onRetry={kpis.refetch} /> : <>
          {[
            { label: "NSE companies",      value: k.n_companies,                            color: "#4ade80",  sub: "Reporting FY2025" },
            { label: "Sector total",       value: `${((k.sector_total_tco2e||0)/1000).toFixed(1)}K`, color: "#4ade80",  sub: "tCO₂e transport" },
            { label: "Avg intensity",      value: (k.avg_intensity||0).toFixed(2),          color: "#fbbf24",  sub: "tCO₂e / KSh M" },
            { label: "NDC gap",            value: `${((k.ndc_gap_tco2e||0)/1000).toFixed(1)}K`, color: "#f87171",  sub: "tCO₂e above target" },
          ].map(item => (
            <div key={item.label} className="rounded-2xl p-5 glass glass-hover relative overflow-hidden"
              style={{ border: "1px solid rgba(34,197,94,0.08)" }}>
              <div className="absolute inset-0 opacity-5"
                style={{ background: `radial-gradient(circle at top right, ${item.color}, transparent 70%)` }} />
              <p className="text-xs uppercase tracking-widest mb-2" style={{ color: "#2d5a3d", fontSize: 9 }}>{item.label}</p>
              <div className="text-2xl font-semibold" style={{ color: item.color, fontFamily: "'DM Sans',sans-serif" }}>{item.value}</div>
              <div className="text-xs mt-1" style={{ color: "#475569" }}>{item.sub}</div>
            </div>
          ))}
        </>}
      </div>

      {/* NDC trajectory from DB */}
      <Card title="Sector NDC alignment · from database · Kenya transport pathway">
        {ndc.loading ? <Loading /> : ndc.error ? <ApiError error={ndc.error} /> : (
          <>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={ndc.data || []} margin={{ top: 4, right: 12, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="gAct" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gNdc" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#0f2340" />
                <XAxis dataKey="year" tick={{ fill: "#2d5a3d", fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#2d5a3d", fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip {...tt} formatter={(v, name) => v != null ? [`${v}K tCO₂e`, name === "actual" ? "Sector actual" : "NDC pathway"] : ["Projected"]} />
                <ReferenceLine y={200} stroke="#ef4444" strokeDasharray="4 2"
                  label={{ value: "2025 NDC", fill: "#f87171", fontSize: 10, position: "insideTopRight" }} />
                <Area type="monotone" dataKey="actual" stroke="#f59e0b" strokeWidth={2}
                  fill="url(#gAct)" dot={{ r: 3, fill: "#f59e0b" }} connectNulls={false} name="actual" />
                <Area type="monotone" dataKey="ndc" stroke="#22c55e" strokeWidth={1.5}
                  fill="url(#gNdc)" dot={false} strokeDasharray="5 3" connectNulls name="ndc" />
              </AreaChart>
            </ResponsiveContainer>
            <div className="flex items-center gap-5 mt-2">
              <div className="flex items-center gap-2">
                <div className="w-5 h-0.5 rounded" style={{ background: "#f59e0b" }} />
                <span className="text-xs" style={{ color: "#475569" }}>Sector actual (DB)</span>
              </div>
              <div className="flex items-center gap-2">
                <svg width="20" height="4"><line x1="0" y1="2" x2="20" y2="2" stroke="#22c55e" strokeWidth="1.5" strokeDasharray="4 2" /></svg>
                <span className="text-xs" style={{ color: "#475569" }}>NDC pathway</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-5 h-0.5" style={{ background: "#ef4444" }} />
                <span className="text-xs" style={{ color: "#475569" }}>2025 target (200K)</span>
              </div>
            </div>
          </>
        )}
      </Card>

      {/* League table + County */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Card title="Sector intensity league table · from DB" badge="Live ranking" badgeColor="amber">
          {league.loading ? <Loading /> : league.error ? <ApiError error={league.error} /> : (
            <div className="space-y-1.5 mt-1 max-h-72 overflow-y-auto">
              {(league.data || []).slice(0, 20).map((l) => {
                const maxIntensity = (league.data || [])[league.data.length - 1]?.intensity || 1;
                const pct = Math.round((l.intensity / maxIntensity) * 100);
                const color = l.quartile === "Q1" ? "#22c55e" : l.quartile === "Q2" ? "#4ade80" :
                              l.quartile === "Q3" ? "#f59e0b" : "#ef4444";
                return (
                  <div key={l.rank} className="flex items-center gap-2 py-1.5 px-1 rounded-lg"
                    style={{ background: l.rank <= 3 ? "rgba(34,197,94,0.04)" : "transparent" }}>
                    <span className="text-xs w-6 text-center font-bold"
                      style={{ color: l.rank <= 3 ? "#4ade80" : "#2d5a3d" }}>{l.rank}</span>
                    <span className="text-xs font-mono w-10 shrink-0" style={{ color: "#64748b" }}>{l.nse_code}</span>
                    <span className="text-xs w-24 shrink-0 truncate" style={{ color: "#475569" }}>{l.sector}</span>
                    <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: "#0f2340" }}>
                      <div className="h-full rounded-full" style={{ width: `${pct}%`, background: color }} />
                    </div>
                    <span className="text-xs font-bold font-mono w-16 text-right" style={{ color }}>
                      {l.intensity?.toFixed(2)} t/M
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </Card>

        <Card title="Emission by county · from DB">
          {county.loading ? <Loading /> : county.error ? <ApiError error={county.error} /> : (
            <div className="space-y-3 mt-1">
              {(county.data || []).slice(0, 8).map((c) => (
                <div key={c.county} className="flex items-center gap-3">
                  <span className="text-xs w-20 shrink-0" style={{ color: "#64748b" }}>{c.county}</span>
                  <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ background: "#0f2340" }}>
                    <div className="h-full rounded-full"
                      style={{ width: `${c.pct}%`, background: c.pct > 20 ? "#22c55e" : "#4ade80" }} />
                  </div>
                  <span className="text-xs font-mono w-20 text-right" style={{ color: "#94a3b8" }}>
                    {c.total_tco2e?.toLocaleString()} t
                  </span>
                  <span className="text-xs w-8 text-right" style={{ color: "#2d5a3d" }}>{c.pct}%</span>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Sector breakdown table */}
      <Card title="Sector breakdown · EPRA sector analytics table from DB">
        {sectors.loading ? <Loading /> : sectors.error ? <ApiError error={sectors.error} /> : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs data-table">
              <thead>
                <tr style={{ borderBottom: "1px solid #0f2340" }}>
                  {["Sector", "Companies", "Total tCO₂e", "Avg intensity", "Min", "Max", "NDC gap tCO₂e", "% national"].map(h => (
                    <th key={h} className="text-left py-2 px-2 font-semibold uppercase tracking-wider"
                      style={{ color: "#2d5a3d", fontSize: 9 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(sectors.data || []).map((row, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #0a1628" }}>
                    <td className="py-2.5 px-2 font-medium" style={{ color: "#94a3b8" }}>{row.sector}</td>
                    <td className="py-2.5 px-2 font-mono text-center" style={{ color: "#475569" }}>{row.n_companies}</td>
                    <td className="py-2.5 px-2 font-mono font-semibold" style={{ color: "#e2e8f0" }}>{row.total_tco2e?.toLocaleString()}</td>
                    <td className="py-2.5 px-2 font-mono" style={{ color: "#e2e8f0" }}>{row.avg_intensity?.toFixed(3)}</td>
                    <td className="py-2.5 px-2 font-mono" style={{ color: "#4ade80" }}>{row.min_intensity?.toFixed(3)}</td>
                    <td className="py-2.5 px-2 font-mono" style={{ color: "#f87171" }}>{row.max_intensity?.toFixed(3)}</td>
                    <td className="py-2.5 px-2 font-mono" style={{ color: row.ndc_gap_tco2e > 0 ? "#f87171" : "#4ade80" }}>
                      {row.ndc_gap_tco2e?.toLocaleString()}
                    </td>
                    <td className="py-2.5 px-2 font-mono" style={{ color: "#94a3b8" }}>{row.sector_pct_of_national}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Policy simulation — calls live ML model */}
      <Card title="EPRA policy simulation · linear regression on 400 training simulations"
        badge="Live ML model · policy_sim_train.csv" badgeColor="blue">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-5">
            {[
              { label: "EV mandate adoption rate", val: ev, set: setEv, max: 100, step: 5, unit: "%" },
              { label: "Fuel economy standard (% above baseline)", val: fe, set: setFe, max: 50,  step: 5, unit: "%" },
              { label: "Remote work policy (% of workforce)",       val: rw, set: setRw, max: 60,  step: 5, unit: "%" },
            ].map(slider => (
              <div key={slider.label}>
                <div className="flex justify-between text-xs mb-2">
                  <span style={{ color: "#64748b" }}>{slider.label}</span>
                  <span className="font-semibold font-mono" style={{ color: "#4ade80" }}>{slider.val}{slider.unit}</span>
                </div>
                <input type="range" min={0} max={slider.max} step={slider.step} value={slider.val}
                  onChange={e => slider.set(+e.target.value)}
                  className="w-full h-1.5 rounded-full appearance-none cursor-pointer"
                  style={{ accentColor: "#22c55e", background: "#0f2340" }}
                />
                <div className="flex justify-between mt-1">
                  <span className="text-xs" style={{ color: "#1e3450" }}>0</span>
                  <span className="text-xs" style={{ color: "#1e3450" }}>{slider.max}{slider.unit}</span>
                </div>
              </div>
            ))}
            <button onClick={runSim} disabled={simRunning}
              className="w-full py-2.5 rounded-xl text-sm font-semibold transition-all"
              style={{
                background: simRunning ? "rgba(34,197,94,0.05)" : "rgba(34,197,94,0.12)",
                color: "#4ade80", border: "1px solid rgba(34,197,94,0.25)",
              }}>
              {simRunning ? "Running ML model…" : "▶ Run simulation"}
            </button>
            {!simResult && (
              <p className="text-xs text-center" style={{ color: "#1e3450" }}>
                Adjust sliders then run — model fitted on policy_sim_train.csv (400 records)
              </p>
            )}
          </div>

          {/* Results */}
          <div className="rounded-2xl p-5 flex flex-col justify-between"
            style={{
              background: sr.ndc_met ? "rgba(34,197,94,0.06)" : simResult ? "rgba(245,158,11,0.05)" : "rgba(10,22,40,0.4)",
              border: `1px solid ${sr.ndc_met ? "rgba(34,197,94,0.25)" : simResult ? "rgba(245,158,11,0.2)" : "#0f2340"}`,
            }}>
            {!simResult ? (
              <div className="flex items-center justify-center h-full py-8">
                <p className="text-xs text-center" style={{ color: "#2d5a3d" }}>
                  Set parameters and click Run simulation<br />to call the live ML model
                </p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-3 gap-3 text-center mb-5">
                  {[
                    { v: `−${((sr.projected_reduction_tco2e||0)/1000).toFixed(1)}K`, l: "tCO₂e reduction" },
                    { v: `${sr.reduction_pct?.toFixed(1)}%`,                         l: "vs baseline" },
                    { v: sr.ndc_met ? "NDC ✓" : `−${((sr.ndc_gap_tco2e||0)/1000).toFixed(1)}K`, l: "NDC gap" },
                  ].map(item => (
                    <div key={item.l}>
                      <div className="text-2xl font-bold font-mono"
                        style={{ color: sr.ndc_met ? "#4ade80" : "#fbbf24", fontFamily: "'DM Sans',sans-serif" }}>
                        {item.v}
                      </div>
                      <div className="text-xs mt-1" style={{ color: "#475569" }}>{item.l}</div>
                    </div>
                  ))}
                </div>
                <div className="mb-4">
                  <div className="flex justify-between text-xs mb-1.5">
                    <span style={{ color: "#475569" }}>Projected total</span>
                    <span className="font-mono font-semibold"
                      style={{ color: sr.ndc_met ? "#4ade80" : "#fbbf24" }}>
                      {((sr.projected_total_tco2e||0)/1000).toFixed(1)}K tCO₂e
                    </span>
                  </div>
                  <div className="h-2.5 rounded-full overflow-hidden" style={{ background: "#0f2340" }}>
                    <div className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.round((sr.projected_total_tco2e || 0) / (sr.baseline_tco2e || 218000) * 100)}%`,
                        background: sr.ndc_met ? "#22c55e" : "#f59e0b",
                      }} />
                  </div>
                </div>
                <p className="text-xs leading-relaxed" style={{ color: "#475569" }}>
                  {sr.ndc_met
                    ? "✓ This policy mix meets the Kenya NDC 2025 transport target."
                    : `Closes ${sr.reduction_pct?.toFixed(0)}% of gap. Additional measures needed.`}
                  <span className="block mt-1" style={{ color: "#2d5a3d" }}>Model: {sr.model}</span>
                </p>
              </>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}
