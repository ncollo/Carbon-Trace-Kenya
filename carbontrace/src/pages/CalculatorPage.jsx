import { api } from "../api/client";
import { useFetch } from "../hooks/useFetch";
import { Loading, ApiError } from "../components/Status";
import Card from "../components/Card";
import KpiCard from "../components/KpiCard";
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";

const tt = {
  contentStyle: {
    background: "#0f1f36", border: "1px solid #1e3450",
    borderRadius: 8, color: "#e2e8f0", fontSize: 11,
    fontFamily: "'DM Sans',sans-serif",
  },
};

const SCOPE_COLORS = ["#22c55e", "#f59e0b", "#3b82f6"];

const CUSTOM_LABEL = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
  const r = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + r * Math.cos(-midAngle * Math.PI / 180);
  const y = cy + r * Math.sin(-midAngle * Math.PI / 180);
  return (
    <text x={x} y={y} fill="#fff" textAnchor="middle"
      dominantBaseline="central" fontSize={11} fontWeight={600}>
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

export default function CalculatorPage() {
  const ghg       = useFetch(api.ghgResults);
  const factors   = useFetch(api.emissionFactors);
  const intensity = useFetch(api.intensityTrendCalc);
  const byVehicle = useFetch(api.scopeByVehicle);

  const g = ghg.data || {};

  const pieData = [
    { name: "Scope 1 Fleet",    value: g.scope1_tco2e   || 0, color: "#22c55e" },
    { name: "S3 Cat 6 Travel",  value: g.s3_cat6_tco2e  || 0, color: "#f59e0b" },
    { name: "S3 Cat 7 Commute", value: g.s3_cat7_tco2e  || 0, color: "#3b82f6" },
  ];

  const total = g.total_tco2e || 0;

  return (
    <div className="space-y-5">

      {/* KPIs from live GHG calculation */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {ghg.loading ? [1,2,3,4].map(i => (
          <div key={i} className="rounded-2xl p-5 glass animate-pulse h-24" />
        )) : <>
          <KpiCard label="Scope 1 — Direct fleet"   value={(g.scope1_tco2e  || 0).toLocaleString()} unit="tCO₂e" />
          <KpiCard label="S3 Cat 6 — Air travel"    value={(g.s3_cat6_tco2e || 0).toLocaleString()} unit="tCO₂e" accent="#f59e0b" />
          <KpiCard label="S3 Cat 7 — Commute"       value={(g.s3_cat7_tco2e || 0).toLocaleString()} unit="tCO₂e" accent="#3b82f6" />
          <KpiCard label="Uncertainty ±95% CI"       value={`±${g.uncertainty_pct_95ci || 0}%`}      unit=""
            delta={`${(g.ci_low_tco2e || 0).toLocaleString()} – ${(g.ci_high_tco2e || 0).toLocaleString()} tCO₂e`}
            accent="#8b5cf6" />
        </>}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

        {/* Scope donut — calculated from live DB */}
        <Card title="Scope breakdown · GHG Protocol · live calculation">
          {ghg.loading ? <Loading /> : ghg.error ? <ApiError error={ghg.error} onRetry={ghg.refetch} /> : (
            <div className="flex items-center gap-4">
              <div style={{ width: 200, height: 200, flexShrink: 0 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="50%"
                      innerRadius={55} outerRadius={90}
                      dataKey="value" labelLine={false} label={CUSTOM_LABEL}>
                      {pieData.map((e, i) => <Cell key={i} fill={e.color} />)}
                    </Pie>
                    <Tooltip {...tt} formatter={v => [`${v.toLocaleString()} tCO₂e`]} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-3 flex-1">
                {pieData.map(d => (
                  <div key={d.name} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-sm shrink-0" style={{ background: d.color }} />
                    <div>
                      <div className="text-xs font-medium" style={{ color: "#94a3b8" }}>{d.name}</div>
                      <div className="text-xs font-mono" style={{ color: "#475569" }}>
                        {d.value.toLocaleString()} tCO₂e
                        {total > 0 && ` · ${(d.value / total * 100).toFixed(1)}%`}
                      </div>
                    </div>
                  </div>
                ))}
                <div className="pt-2 border-t" style={{ borderColor: "#0f2340" }}>
                  <div className="text-xs" style={{ color: "#2d5a3d" }}>Grand total</div>
                  <div className="text-lg font-semibold font-mono" style={{ color: "#4ade80" }}>
                    {total.toLocaleString()} tCO₂e
                  </div>
                  <div className="text-xs mt-0.5" style={{ color: "#2d5a3d" }}>
                    {g.defra_ef_version} · {g.ipcc_gwp_version}
                  </div>
                </div>
              </div>
            </div>
          )}
        </Card>

        {/* Methodology from live GHG response */}
        <Card title="Calculation methodology · live">
          {ghg.loading ? <Loading /> : (
            <div className="space-y-2">
              {[
                { scope: "Scope 1",  color: "#22c55e", std: "GHG Protocol Corporate", ef: `DEFRA 2024 · Kenya ×${g.kenya_road_adj || 1.18}`, tier: "Tier 2" },
                { scope: "S3 Cat 6", color: "#f59e0b", std: "GHG Protocol Value Chain", ef: "DEFRA 2024 + RFI 1.9", tier: "Tier 2" },
                { scope: "S3 Cat 7", color: "#3b82f6", std: "GHG Protocol Value Chain", ef: "HR survey Tier 1", tier: "Tier 1" },
              ].map(m => (
                <div key={m.scope} className="p-3 rounded-xl"
                  style={{ background: "rgba(10,22,40,0.6)", border: "1px solid #0f2340" }}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold" style={{ color: m.color }}>{m.scope}</span>
                    <span className="text-xs px-2 py-0.5 rounded font-mono"
                      style={{ background: "rgba(34,197,94,0.08)", color: "#22c55e" }}>{m.tier}</span>
                  </div>
                  <div className="text-xs" style={{ color: "#94a3b8" }}>{m.std}</div>
                  <div className="text-xs mt-0.5" style={{ color: "#475569" }}>EF: {m.ef}</div>
                </div>
              ))}
              <div className="p-3 rounded-xl"
                style={{ background: "rgba(139,92,246,0.06)", border: "1px solid rgba(139,92,246,0.2)" }}>
                <div className="text-xs font-bold mb-1" style={{ color: "#a78bfa" }}>Bayesian uncertainty · PyMC</div>
                <div className="text-xs" style={{ color: "#94a3b8" }}>
                  ±{g.uncertainty_pct_95ci || 0}% at 95% CI
                </div>
                <div className="text-xs mt-0.5" style={{ color: "#475569" }}>
                  {(g.ci_low_tco2e || 0).toLocaleString()} – {(g.ci_high_tco2e || 0).toLocaleString()} tCO₂e
                </div>
                <div className="text-xs mt-0.5" style={{ color: "#475569" }}>
                  KETRACO grid EF: {g.ketraco_grid_ef || 0.392} kgCO₂e/kWh
                </div>
              </div>
            </div>
          )}
        </Card>
      </div>

      {/* Intensity trend */}
      <Card title="Emission intensity trend · from DB — tCO₂e per KSh M revenue">
        {intensity.loading ? <Loading /> : intensity.error ? <ApiError error={intensity.error} /> : (
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={intensity.data || []} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#0f2340" />
              <XAxis dataKey="year" tick={{ fill: "#2d5a3d", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#2d5a3d", fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip {...tt} formatter={v => [`${v.toFixed(4)} t/KSh M`, "Intensity"]} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]} fill="#22c55e" opacity={0.85} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </Card>

      {/* Emission factors from DB */}
      <Card title="Emission factor register · from database · DEFRA 2024" badge="Kenya-calibrated" badgeColor="green">
        {factors.loading ? <Loading /> : factors.error ? <ApiError error={factors.error} /> : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs data-table">
              <thead>
                <tr style={{ borderBottom: "1px solid #0f2340" }}>
                  {["ID", "Category", "EF (kgCO₂e)", "Kenya Adj", "Adj EF", "Source", "Tier", "Scope"].map(h => (
                    <th key={h} className="text-left py-2 px-2 font-semibold uppercase tracking-wider"
                      style={{ color: "#2d5a3d", fontSize: 9 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(factors.data || []).map((f, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #0a1628" }}>
                    <td className="py-2 px-2 font-mono" style={{ color: "#2d5a3d" }}>{f.ef_id}</td>
                    <td className="py-2 px-2" style={{ color: "#94a3b8" }}>{f.category}</td>
                    <td className="py-2 px-2 font-mono font-semibold" style={{ color: "#4ade80" }}>
                      {f.ef_kgco2e_per_l || f.ef_kgco2e_per_kwh || f.ef_kgco2e_per_pkm || "—"}
                    </td>
                    <td className="py-2 px-2 font-mono" style={{ color: "#fbbf24" }}>×{f.kenya_adj_factor}</td>
                    <td className="py-2 px-2 font-mono" style={{ color: "#4ade80" }}>{f.adjusted_ef}</td>
                    <td className="py-2 px-2" style={{ color: "#475569" }}>{f.source}</td>
                    <td className="py-2 px-2">
                      <span className="px-1.5 py-0.5 rounded text-xs"
                        style={{ background: "rgba(34,197,94,0.08)", color: "#22c55e" }}>{f.tier}</span>
                    </td>
                    <td className="py-2 px-2" style={{ color: "#475569" }}>{f.scope}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* By vehicle class from DB */}
      <Card title="Scope 1 breakdown by vehicle class · aggregated from DB">
        {byVehicle.loading ? <Loading /> : byVehicle.error ? <ApiError error={byVehicle.error} /> : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs data-table">
              <thead>
                <tr style={{ borderBottom: "1px solid #0f2340" }}>
                  {["Vehicle class", "Units", "Total tCO₂e", "Avg EF (kgCO₂e/L)", "Kenya adj"].map(h => (
                    <th key={h} className="text-left py-2 px-2 font-semibold uppercase tracking-wider"
                      style={{ color: "#2d5a3d", fontSize: 9 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(byVehicle.data || []).map((r, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #0a1628" }}>
                    <td className="py-2 px-2 font-medium" style={{ color: "#94a3b8" }}>
                      {r.vehicle_class?.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}
                    </td>
                    <td className="py-2 px-2 font-mono" style={{ color: "#475569" }}>{r.units}</td>
                    <td className="py-2 px-2 font-mono font-semibold" style={{ color: "#4ade80" }}>
                      {r.total_tco2e?.toLocaleString()}
                    </td>
                    <td className="py-2 px-2 font-mono" style={{ color: "#fbbf24" }}>{r.avg_ef}</td>
                    <td className="py-2 px-2 font-mono" style={{ color: "#fbbf24" }}>+{((r.kenya_adj - 1) * 100).toFixed(0)}%</td>
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
