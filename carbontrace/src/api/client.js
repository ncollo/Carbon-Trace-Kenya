const BASE = "http://localhost:8002/api";

async function get(path) {
  const r = await fetch(`${BASE}${path}`);
  if (!r.ok) throw new Error(`API error ${r.status}: ${path}`);
  return r.json();
}

async function post(path, body) {
  const r = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`API error ${r.status}: ${path}`);
  return r.json();
}

async function patch(path) {
  const r = await fetch(`${BASE}${path}`, { method: "PATCH" });
  if (!r.ok) throw new Error(`API error ${r.status}: ${path}`);
  return r.json();
}

export const api = {
  health: () => get("/health"),

  // Overview
  kpis:            () => get("/overview/kpis"),
  quarterlyTrend:  () => get("/overview/quarterly-trend"),
  scopeBreakdown:  () => get("/overview/scope-breakdown"),
  fleetByClass:    () => get("/overview/fleet-by-class"),
  companies:       () => get("/overview/companies"),
  intensityTrend:  () => get("/overview/intensity-trend"),

  // Ingestion
  files:           () => get("/ingestion/files"),
  extractionStats: () => get("/ingestion/extraction-stats"),
  uploadFile: (formData) =>
    fetch(`${BASE}/ingestion/upload`, { method: "POST", body: formData })
      .then(r => r.json()),
  uploadImage: (formData) =>
    fetch(`${BASE}/ingestion/upload-image`, { method: "POST", body: formData })
      .then(r => r.json()),
  chat: (message, history = []) => post("/chat", { message, history }),

  // Reconcile
  flags:        (status = "pending") => get(`/reconcile/flags?status=${status}&limit=50`),
  resolveFlag:  (id) => patch(`/reconcile/flags/${id}/resolve`),
  quality:      () => get("/reconcile/quality"),
  validationLog:() => get("/reconcile/validation-log?limit=20"),
  runModel:     (payload) => post("/reconcile/run-model", payload),

  // Calculator
  ghgResults:    (nse = "") => get(`/calculator/results${nse ? `?nse_code=${nse}` : ""}`),
  emissionFactors:() => get("/calculator/emission-factors"),
  intensityTrendCalc:() => get("/calculator/intensity-trend"),
  scopeByVehicle:() => get("/calculator/scope-by-vehicle"),

  // Report
  reportSummary:     (nse = "") => get(`/report/summary${nse ? `?nse_code=${nse}` : ""}`),
  narrativeSamples:  () => get("/report/narrative-samples?n=5"),

  // EPRA
  epraKpis:       () => get("/epra/kpis"),
  ndcTrajectory:  () => get("/epra/ndc-trajectory"),
  sectorBreakdown:() => get("/epra/sector-breakdown"),
  leagueTable:    () => get("/epra/league-table"),
  countyDist:     () => get("/epra/county-distribution"),
  simulate:       (body) => post("/epra/simulate", body),
};
