import { AppProvider, useApp } from "./context/AppContext";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import OverviewPage from "./pages/OverviewPage";
import IngestionPage from "./pages/IngestionPage";
import ReconcilePage from "./pages/ReconcilePage";
import CalculatorPage from "./pages/CalculatorPage";
import ReportPage from "./pages/ReportPage";
import EpraPage from "./pages/EpraPage";

const PAGE_META = {
  overview:   { title:"Emission Overview",               sub:"FY 2025 · GHG Protocol Corporate Standard · Kenya-calibrated · DEFRA 2024" },
  ingestion:  { title:"Data Ingestion · AI Extraction",  sub:"LayoutLM fine-tuned · GPT-4o Vision · RapidFuzz schema-matching · pdfplumber" },
  reconcile:  { title:"Cross-Source Reconciliation",     sub:"Isolation Forest anomaly detection · GPS cross-validation · fraud signal analysis" },
  calculator: { title:"GHG Protocol Engine",             sub:"DEFRA 2024 · KETRACO 0.392 kgCO₂e/kWh · NTSA +18% road adj · IPCC AR6 · PyMC ±4.8%" },
  report:     { title:"NSE Disclosure Report",           sub:"PDF + XBRL (IFRS S2) · GRI 305 · NSE ESG Guidance 2021 · GPT-4o mini narrative" },
  epra:       { title:"EPRA Sector Analytics",           sub:"PySyft federated learning · NDC alignment · policy simulation · county mapping" },
};

function Shell() {
  const { activePage } = useApp();
  const meta = PAGE_META[activePage];
  const pages = { overview:<OverviewPage/>, ingestion:<IngestionPage/>, reconcile:<ReconcilePage/>, calculator:<CalculatorPage/>, report:<ReportPage/>, epra:<EpraPage/> };
  return (
    <div className="flex h-full overflow-hidden" style={{ background:"#060e1a" }}>
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Topbar title={meta.title} sub={meta.sub} />
        <main className="flex-1 overflow-y-auto grid-bg">
          <div className="p-6 stagger">{pages[activePage]}</div>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return <AppProvider><Shell /></AppProvider>;
}
