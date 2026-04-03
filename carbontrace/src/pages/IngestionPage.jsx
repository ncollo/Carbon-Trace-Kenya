import { useState, useRef } from "react";
import { api } from "../api/client";
import { useFetch } from "../hooks/useFetch";
import { Loading, ApiError } from "../components/Status";
import Card from "../components/Card";

const STEPS = [
  { n:1, label:"Upload data",         status:"done"    },
  { n:2, label:"AI extract",          status:"done"    },
  { n:3, label:"Reconcile anomalies", status:"active"  },
  { n:4, label:"Calculate GHG",       status:"pending" },
  { n:5, label:"Generate report",     status:"pending" },
];

function StepNode({ status, n }) {
  if (status === "done")
    return <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold z-10 relative"
      style={{ background:"#22c55e", color:"#030712" }}>✓</div>;
  if (status === "active")
    return <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold z-10 relative animate-pulse"
      style={{ background:"#f59e0b", color:"#030712" }}>{n}</div>;
  return <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs z-10 relative"
    style={{ background:"#0a1628", border:"1px solid #1e3450", color:"#2d5a3d" }}>{n}</div>;
}

const TYPE_COLORS = {
  PDF: { bg:"rgba(239,68,68,0.1)",   color:"#f87171" },
  XLS: { bg:"rgba(34,197,94,0.1)",   color:"#4ade80" },
  CSV: { bg:"rgba(245,158,11,0.1)",  color:"#fbbf24" },
  IMG: { bg:"rgba(139,92,246,0.1)",  color:"#a78bfa" },
};

export default function IngestionPage() {
  const files      = useFetch(api.files);
  const extraction = useFetch(api.extractionStats);

  const [dragging, setDragging]   = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState(null);
  const fileRef = useRef();

  const doUpload = async (fileObj) => {
    if (!fileObj) return;
    setUploading(true);
    setUploadMsg(null);
    const form = new FormData();
    form.append("file", fileObj);
    form.append("nse_code", "UPLOAD");
    try {
      const result = await api.uploadFile(form);
      setUploadMsg(`✓ ${result.filename} — ${result.records_extracted} records extracted via ${result.method}`);
      await files.refetch();
      await extraction.refetch();
    } catch (e) {
      setUploadMsg(`Error: ${e.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault(); setDragging(false);
    doUpload(e.dataTransfer.files[0]);
  };

  return (
    <div className="space-y-5">

      {/* Pipeline stepper */}
      <Card title="AI pipeline · 5-module processing">
        <div className="flex items-start gap-0 mt-3">
          {STEPS.map((s, i) => (
            <div key={s.n} className="flex-1 flex flex-col items-center relative">
              {i < STEPS.length - 1 && (
                <div className="absolute top-3.5 left-1/2 w-full h-0.5 z-0"
                  style={{ background: s.status === "done" ? "#22c55e" : "#0f2340" }} />
              )}
              <StepNode status={s.status} n={s.n} />
              <div className="text-xs text-center mt-2 leading-tight"
                style={{ color: s.status === "active" ? "#fbbf24" : s.status === "done" ? "#22c55e" : "#1e3450" }}>
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Upload zone */}
      <div
        onDragOver={e => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileRef.current?.click()}
        className="rounded-2xl p-10 text-center cursor-pointer transition-all duration-300 relative overflow-hidden"
        style={{
          background: dragging ? "rgba(34,197,94,0.06)" : "rgba(15,31,54,0.4)",
          border: `2px dashed ${dragging ? "#22c55e" : "#0f2340"}`,
        }}
      >
        <input ref={fileRef} type="file" accept=".csv,.xlsx,.xls,.pdf"
          className="hidden" onChange={e => doUpload(e.target.files[0])} />
        {uploading ? (
          <div>
            <div className="w-6 h-6 rounded-full border-2 border-transparent border-t-green-500 animate-spin mx-auto mb-2" />
            <div className="text-sm" style={{ color:"#4ade80" }}>Uploading & extracting…</div>
          </div>
        ) : uploadMsg ? (
          <div>
            <div className="text-2xl mb-2">✓</div>
            <div className="text-sm font-medium" style={{ color:"#4ade80" }}>{uploadMsg}</div>
          </div>
        ) : (
          <>
            <div className="text-3xl mb-3 opacity-40">⬆</div>
            <div className="text-sm font-semibold mb-1" style={{ color:"#94a3b8" }}>
              Drop a CSV / Excel / PDF file here to ingest
            </div>
            <div className="text-xs" style={{ color:"#1e3450" }}>
              Fuel card CSV · GPS Excel export · SAP travel CSV · Commute survey — auto-detected and ingested into DB
            </div>
          </>
        )}
      </div>

      {/* Files from DB + Extraction stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Card title="Ingested files · from database" badge={`${(files.data||[]).length} logged`}>
          {files.loading ? <Loading /> : files.error ? <ApiError error={files.error} onRetry={files.refetch} /> : (
            <div className="space-y-2">
              {(files.data || []).length === 0 ? (
                <p className="text-xs text-center py-4" style={{ color: "#2d5a3d" }}>
                  No uploads yet — drop a file above to add records to the DB
                </p>
              ) : (files.data || []).map(f => {
                const tc = TYPE_COLORS[f.file_type] || TYPE_COLORS.CSV;
                return (
                  <div key={f.id} className="flex items-center gap-3 px-3 py-2.5 rounded-xl"
                    style={{ background:"rgba(10,22,40,0.6)", border:"1px solid #0f2340" }}>
                    <div className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold shrink-0"
                      style={{ background:tc.bg, color:tc.color }}>{f.file_type}</div>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-medium truncate" style={{ color:"#94a3b8" }}>{f.filename}</div>
                      <div className="text-xs" style={{ color:"#2d5a3d" }}>
                        {(f.file_size/1024).toFixed(1)} KB · {f.method} · {f.records_extracted} records
                      </div>
                    </div>
                    <span className="text-xs px-2 py-0.5 rounded-md shrink-0"
                      style={f.status === "done"
                        ? { background:"rgba(34,197,94,0.1)", color:"#4ade80" }
                        : f.status === "error"
                        ? { background:"rgba(239,68,68,0.1)", color:"#f87171" }
                        : { background:"rgba(245,158,11,0.1)", color:"#fbbf24" }}>
                      {f.status === "done" ? "Extracted ✓" : f.status === "error" ? "Error" : "Processing…"}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </Card>

        <Card title="Extracted fields · from DB record counts" badge="Live stats" badgeColor="blue">
          {extraction.loading ? <Loading /> : extraction.error ? <ApiError error={extraction.error} /> : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr style={{ borderBottom:"1px solid #0f2340" }}>
                    {["Field","Records","Confidence","Source"].map(h => (
                      <th key={h} className="text-left py-2 px-2 font-semibold uppercase tracking-wider"
                        style={{ color:"#2d5a3d", fontSize:9 }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(extraction.data || []).map((e, i) => (
                    <tr key={i} style={{ borderBottom:"1px solid #0a1628" }}>
                      <td className="py-2 px-2 font-medium" style={{ color:"#94a3b8" }}>{e.field}</td>
                      <td className="py-2 px-2 font-mono" style={{ color:"#e2e8f0" }}>{e.records?.toLocaleString()}</td>
                      <td className="py-2 px-2 font-mono font-semibold" style={{ color:"#4ade80" }}>{e.confidence}</td>
                      <td className="py-2 px-2" style={{ color:"#475569", fontSize:10 }}>{e.source}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>

      {/* Dataset info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {[
          { icon:"◈", title:"SQLite database", sub:"carbontrace.db — seeded from 12,657 CSV records across all modules. Fuel cards, GPS logs, travel, commute, GHG summaries, anomalies, EFs.", badge:"Live DB" },
          { icon:"◉", title:"Isolation Forest", sub:"Trained on 2,400 clean fuel records. 89.2% anomaly detection rate on test split. Model saved as isolation_forest.pkl.", badge:"89.2% accuracy" },
          { icon:"◎", title:"Policy regression", sub:"Linear model fitted on 400 policy simulation training records. Predicts sector emission reduction from EV/fuel economy/remote work levers.", badge:"400 training sims" },
        ].map(item => (
          <div key={item.title} className="rounded-2xl p-4 glass"
            style={{ border:"1px solid rgba(34,197,94,0.08)" }}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span style={{ color:"#4ade80", fontSize:18 }}>{item.icon}</span>
                <span className="text-sm font-semibold" style={{ color:"#e2e8f0" }}>{item.title}</span>
              </div>
              <span className="text-xs px-2 py-0.5 rounded"
                style={{ background:"rgba(34,197,94,0.08)", color:"#22c55e", fontSize:10 }}>{item.badge}</span>
            </div>
            <p className="text-xs leading-relaxed" style={{ color:"#475569" }}>{item.sub}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
