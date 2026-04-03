import { createContext, useContext, useState } from "react";

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [activePage, setActivePage] = useState("overview");
  const [anomalyFlags, setAnomalyFlags] = useState(["KNP-TRK-041","KNP-CAR-019","KNP-SUV-007"]);
  const [pipelineStage, setPipelineStage] = useState(2);
  const [processingFiles, setProcessingFiles] = useState([
    { id:1, name:"Total_Kenya_FuelCard_Q1-Q4_2025.pdf", type:"PDF", size:"2.4 MB", status:"done", method:"LayoutLM" },
    { id:2, name:"Fleet_GPS_Log_2025_Nairobi.xlsx",      type:"XLS", size:"1.1 MB", status:"done", method:"Schema-match" },
    { id:3, name:"SAP_Travel_Bookings_FY2025.csv",       type:"CSV", size:"380 KB", status:"done", method:"Pandas" },
    { id:4, name:"Scanned_Receipts_Q3_batch.zip",        type:"IMG", size:"14.2 MB",status:"done", method:"GPT-4o Vision" },
    { id:5, name:"HR_Commute_Survey_2025.xlsx",          type:"XLS", size:"220 KB", status:"processing", method:"Pandas" },
  ]);

  const resolveAnomaly = (id) => setAnomalyFlags(f => f.filter(x => x !== id));

  return (
    <AppContext.Provider value={{ activePage, setActivePage, anomalyFlags, resolveAnomaly, pipelineStage, setPipelineStage, processingFiles }}>
      {children}
    </AppContext.Provider>
  );
}

export const useApp = () => useContext(AppContext);
