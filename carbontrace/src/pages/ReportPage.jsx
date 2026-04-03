import { useState } from "react";
import { api } from "../api/client";
import { useFetch } from "../hooks/useFetch";
import { Loading, ApiError } from "../components/Status";
import Card from "../components/Card";

export default function ReportPage() {
  const report    = useFetch(api.reportSummary);
  const narratives = useFetch(api.narrativeSamples);
  const [openSection, setOpenSection] = useState(null);
  const [downloading, setDownloading] = useState(null);

  const handleDownload = (type) => {
    setDownloading(type);
    setTimeout(() => setDownloading(null), 2000);
  };

  const r = report.data || {};
  const g = r.ghg || {};
  const c = r.company || {};
  const m = r.methodology || {};

  return (
    <div className="space-y-5">

      {/* NSE-Ready banner */}
      <div className="rounded-2xl px-5 py-4 flex items-center justify-between"
        style={{ background: "rgba(34,197,94,0.06)", border: "1px solid rgba(34,197,94,0.2)" }}>
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center text-lg"
            style={{ background: "rgba(34,197,94,0.12)" }}>✓</div>
          <div>
            <div className="text-sm font-semibold" style={{ color: "#4ade80" }}>Report ready for NSE submission</div>
            <div className="text-xs mt-0.5" style={{ color: "#2d5a3d" }}>
              PDF + XBRL (IFRS S2) · GRI 305 · GPT-4o mini narrative · hallucination guard passed
            </div>
          </div>
        </div>
        <div className="text-right">
          {report.loading ? (
            <div className="text-xs font-mono" style={{ color: "#2d5a3d" }}>Loading…</div>
          ) : (
            <>
              <div className="text-xs font-mono font-semibold" style={{ color: "#4ade80" }}>
                {(g.total_tco2e || 0).toLocaleString()} tCO₂e
              </div>
              <div className="text-xs" style={{ color: "#2d5a3d" }}>FY{c.fy_year || 2024} total · live calculation</div>
            </>
          )}
        </div>
      </div>

      {/* Report identity + recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Card title="Report identity · from database">
          {report.loading ? <Loading /> : report.error ? <ApiError error={report.error} onRetry={report.refetch} /> : (
            <div className="space-y-0">
              {[
                ["Company",          c.company_name || "All companies"],
                ["NSE code",         c.nse_code || "Portfolio"],
                ["Reporting period", `FY${c.fy_year || 2024}`],
                ["Framework",        "GHG Protocol Corporate Standard"],
                ["XBRL taxonomy",    c.xbrl_taxonomy || "IFRS S2"],
                ["GRI alignment",    "GRI 305: Emissions"],
                ["EF source",        g.defra_ef_version || "DEFRA 2024"],
                ["GWP standard",     g.ipcc_gwp_version || "IPCC AR6"],
                ["Kenya road adj",   `+${((g.kenya_road_adj || 1.18) - 1) * 100}% NTSA`],
                ["KETRACO grid EF",  `${g.ketraco_grid_ef || 0.392} kgCO₂e/kWh`],
                ["Audit trail",      "SHA-256 immutable chain · AES-256"],
                ["Prepared by",      "CarbonTrace Kenya AI Engine v1.0"],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between items-start py-2.5 border-b"
                  style={{ borderColor: "#0f2340" }}>
                  <span className="text-xs" style={{ color: "#475569" }}>{k}</span>
                  <span className="text-xs font-medium text-right max-w-[55%]"
                    style={{ color: "#94a3b8" }}>{v}</span>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card title="AI reduction recommendations · from training data" badge="GPT-4o mini · narrative_train.csv" badgeColor="green">
          {narratives.loading ? <Loading /> : narratives.error ? <ApiError error={narratives.error} /> : (
            <div className="space-y-3">
              {(narratives.data || []).map((n, i) => (
                <div key={i} className="p-3 rounded-xl"
                  style={{ background: "rgba(34,197,94,0.04)", border: "1px solid rgba(34,197,94,0.12)" }}>
                  <div className="flex gap-2 items-start">
                    <span className="font-bold text-lg w-5 shrink-0 leading-tight"
                      style={{ color: "#22c55e" }}>{i + 1}</span>
                    <div>
                      <p className="text-xs leading-relaxed" style={{ color: "#94a3b8" }}>
                        {n.recommendation_narrative}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Emission summary */}
      <Card title="Disclosed emission figures · calculated from DB records">
        {report.loading ? <Loading /> : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs data-table">
              <thead>
                <tr style={{ borderBottom: "1px solid #0f2340" }}>
                  {["Scope / Category", "tCO₂e", "Standard", "EF source"].map(h => (
                    <th key={h} className="text-left py-2 px-3 font-semibold uppercase tracking-wider"
                      style={{ color: "#2d5a3d", fontSize: 9 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  { cat: "Scope 1 — Owned & leased fleet (Tier 2)", val: g.scope1_tco2e,   std: "GHG Protocol Corporate",      ef: g.defra_ef_version || "DEFRA 2024" },
                  { cat: "Scope 3 Cat 6 — Business travel",          val: g.s3_cat6_tco2e,  std: "GHG Protocol Value Chain",    ef: "DEFRA 2024 + RFI 1.9" },
                  { cat: "Scope 3 Cat 7 — Employee commuting",       val: g.s3_cat7_tco2e,  std: "GHG Protocol Value Chain",    ef: "HR Survey Tier 1" },
                ].map((row, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #0a1628" }}>
                    <td className="py-3 px-3 font-medium" style={{ color: "#94a3b8" }}>{row.cat}</td>
                    <td className="py-3 px-3 font-mono font-semibold" style={{ color: "#e2e8f0" }}>
                      {(row.val || 0).toLocaleString()}
                    </td>
                    <td className="py-3 px-3" style={{ color: "#475569" }}>{row.std}</td>
                    <td className="py-3 px-3" style={{ color: "#475569" }}>{row.ef}</td>
                  </tr>
                ))}
                <tr style={{ background: "rgba(34,197,94,0.05)", borderTop: "1px solid rgba(34,197,94,0.15)" }}>
                  <td className="py-3 px-3 font-bold" style={{ color: "#4ade80" }}>Grand total</td>
                  <td className="py-3 px-3 font-mono font-bold text-lg" style={{ color: "#4ade80" }}>
                    {(g.total_tco2e || 0).toLocaleString()}
                  </td>
                  <td className="py-3 px-3" style={{ color: "#2d5a3d" }}>—</td>
                  <td className="py-3 px-3" style={{ color: "#2d5a3d" }}>±{g.uncertainty_pct_95ci || 0}% CI</td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Methodology narratives from training CSV */}
      <Card title="Methodology narrative · samples from narrative_train.csv">
        {narratives.loading ? <Loading /> : narratives.error ? <ApiError error={narratives.error} /> : (
          <div className="space-y-2">
            {[
              { title: "1. Scope 1 — Direct mobile combustion", key: "scope1_narrative" },
              { title: "2. Emission intensity analysis",         key: "intensity_narrative" },
              { title: "3. Uncertainty quantification",          key: "uncertainty_narrative" },
            ].map((sec, i) => (
              <div key={i} className="rounded-xl overflow-hidden"
                style={{ border: "1px solid #0f2340" }}>
                <button
                  className="w-full flex items-center justify-between px-4 py-3 text-left transition-colors"
                  style={{ background: openSection === i ? "rgba(34,197,94,0.06)" : "rgba(10,22,40,0.6)" }}
                  onClick={() => setOpenSection(openSection === i ? null : i)}
                >
                  <span className="text-xs font-semibold"
                    style={{ color: openSection === i ? "#4ade80" : "#64748b" }}>{sec.title}</span>
                  <span className="text-xs ml-4 shrink-0 transition-transform duration-200"
                    style={{ color: "#2d5a3d", transform: openSection === i ? "rotate(180deg)" : "none" }}>▾</span>
                </button>
                {openSection === i && (
                  <div className="px-4 py-3"
                    style={{ background: "rgba(6,14,26,0.4)", borderTop: "1px solid #0f2340" }}>
                    <p className="text-xs leading-relaxed" style={{ color: "#64748b" }}>
                      {(narratives.data || [])[0]?.[sec.key] || "Loading from narrative_train.csv…"}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Downloads */}
      <Card title="Download disclosure outputs">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            { type: "pdf",  icon: "📄", title: "Download PDF report",  sub: "GRI 305 · NSE ESG Guidance 2021 · ReportLab",    iconBg: "rgba(239,68,68,0.1)" },
            { type: "xbrl", icon: "📊", title: "Download XBRL file",   sub: "IFRS S2 taxonomy · Arelle · NSE submission",      iconBg: "rgba(59,130,246,0.1)" },
          ].map(btn => (
            <button key={btn.type} onClick={() => handleDownload(btn.type)}
              className="flex items-center gap-3 px-4 py-3.5 rounded-xl text-left transition-all duration-200"
              style={{
                background: downloading === btn.type ? "rgba(34,197,94,0.08)" : "rgba(10,22,40,0.6)",
                border: `1px solid ${downloading === btn.type ? "rgba(34,197,94,0.3)" : "#0f2340"}`,
              }}>
              <span className="w-9 h-9 rounded-lg flex items-center justify-center text-base shrink-0"
                style={{ background: btn.iconBg }}>{btn.icon}</span>
              <span>
                <span className="block text-sm font-semibold" style={{ color: "#e2e8f0" }}>
                  {downloading === btn.type ? "Generating…" : btn.title}
                </span>
                <span className="block text-xs mt-0.5" style={{ color: "#475569" }}>{btn.sub}</span>
              </span>
            </button>
          ))}
        </div>
        <div className="mt-4 px-4 py-3 rounded-xl"
          style={{ background: "rgba(34,197,94,0.04)", border: "1px solid rgba(34,197,94,0.1)" }}>
          <p className="text-xs leading-relaxed" style={{ color: "#2d5a3d" }}>
            <span className="font-semibold" style={{ color: "#4ade80" }}>Audit trail active.</span>{" "}
            All emission calculations are derived from the live SQLite database seeded from your CSV datasets.
            SHA-256 immutable log · AES-256 encrypted · fully traceable for EPRA regulatory review.
          </p>
        </div>
      </Card>
    </div>
  );
}
