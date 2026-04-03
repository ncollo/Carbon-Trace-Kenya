export const DEFRA_EF = {
  diesel_truck: 2.640, diesel_van: 2.640, petrol_saloon: 2.311,
  petrol_suv: 2.311, petrol_4wd: 2.640, petrol_bike: 2.296,
  diesel_bus: 2.640, ev: 0,
};
export const KETRACO_EF = 0.392;
export const KENYA_ROAD_ADJ = 1.18;
export const GWP = { CO2: 1.0, CH4: 27.9, N2O: 273.0 };

export const NSE_COMPANIES = [
  { id:"NSE-001", name:"Kenya Power & Lighting Co.", code:"KPLC", sector:"Energy & Petroleum", county:"Nairobi", scope1:2989, s3c6:1157, s3c7:675, total:4821, intensity:12.4, fy23:4537, fleet:131, revenue:388.8 },
  { id:"NSE-002", name:"Safaricom PLC", code:"SCOM", sector:"Telecommunications", county:"Nairobi", scope1:3421, s3c6:980, s3c7:820, total:5221, intensity:8.1, fy23:5544, fleet:210, revenue:644.6 },
  { id:"NSE-003", name:"Equity Group Holdings", code:"EQTY", sector:"Banking & Finance", county:"Nairobi", scope1:1840, s3c6:640, s3c7:480, total:2960, intensity:5.2, fy23:3108, fleet:88, revenue:569.2 },
  { id:"NSE-004", name:"East African Breweries", code:"EABL", sector:"Manufacturing", county:"Nairobi", scope1:4120, s3c6:1340, s3c7:920, total:6380, intensity:18.7, fy23:5902, fleet:245, revenue:341.2 },
  { id:"NSE-005", name:"KCB Group PLC", code:"KCB", sector:"Banking & Finance", county:"Nairobi", scope1:2240, s3c6:720, s3c7:560, total:3520, intensity:6.8, fy23:3740, fleet:112, revenue:517.6 },
  { id:"NSE-006", name:"Nation Media Group", code:"NMG", sector:"Media", county:"Nairobi", scope1:890, s3c6:320, s3c7:240, total:1450, intensity:9.2, fy23:1320, fleet:56, revenue:157.6 },
  { id:"NSE-007", name:"Bamburi Cement", code:"BAMB", sector:"Construction", county:"Mombasa", scope1:8920, s3c6:2140, s3c7:1120, total:12180, intensity:31.2, fy23:11840, fleet:380, revenue:390.4 },
];

export const QUARTERLY_TREND = [
  { q:"Q1 23", val:1050 }, { q:"Q2 23", val:1120 }, { q:"Q3 23", val:1090 }, { q:"Q4 23", val:1180 },
  { q:"Q1 24", val:1130 }, { q:"Q2 24", val:1160 }, { q:"Q3 24", val:1200 }, { q:"Q4 24", val:1080 },
  { q:"Q1 25", val:1140 }, { q:"Q2 25", val:1210 }, { q:"Q3 25", val:1250 }, { q:"Q4 25", val:1221 },
];

export const FLEET_DATA = [
  { name:"Heavy Diesel", type:"Trucks · 23 units", val:1142, pct:78, color:"#22c55e" },
  { name:"Mid Petrol",   type:"Saloons · 67 units", val:761, pct:52, color:"#4ade80" },
  { name:"SUV / 4WD",   type:"Field · 41 units",   val:534, pct:36, color:"#f59e0b" },
  { name:"EV Fleet",    type:"KETRACO 0.392 kWh",  val:178, pct:12, color:"#3b82f6" },
  { name:"Motorbikes",  type:"Last-mile · 88",      val:374, pct:25, color:"#8b5cf6" },
];

export const SCOPE_DATA = [
  { name:"Scope 1",   value:2989, color:"#22c55e", pct:62 },
  { name:"S3 Cat 6",  value:1157, color:"#f59e0b", pct:24 },
  { name:"S3 Cat 7",  value:675,  color:"#3b82f6", pct:14 },
];

export const INTENSITY_TREND = [
  { year:"FY21", val:16.8 }, { year:"FY22", val:15.9 },
  { year:"FY23", val:14.7 }, { year:"FY24", val:12.8 }, { year:"FY25", val:12.4 },
];

export const ANOMALY_FLAGS = [
  { id:"KNP-TRK-041", date:"Nov 14", type:"Physical impossibility", desc:"Declared 80 L diesel · GPS: 122 km · Max range at rated: 68 km", impact:"+18.4 tCO₂e overstatement", confidence:"97%", severity:"high" },
  { id:"KNP-CAR-019", date:"Sep 03", type:"Tank overflow",          desc:"Receipt: 55 L · Tank capacity: 45 L · Refuel already logged same day", impact:"+12.9 tCO₂e overstatement", confidence:"99%", severity:"high" },
  { id:"KNP-SUV-007", date:"Jul 22", type:"Fraud signal",           desc:"GPS: 0 km travel · Fuel record: 34 L consumed", impact:"+8.1 tCO₂e overstatement", confidence:"99%", severity:"critical" },
];

export const EMISSION_FACTORS = [
  { id:"EF-001", category:"Heavy diesel truck",   ef:"2.640", adj:"+18%", source:"DEFRA 2024", tier:"Tier 2", scope:"Scope 1" },
  { id:"EF-002", category:"Diesel van / LGV",     ef:"2.640", adj:"+18%", source:"DEFRA 2024", tier:"Tier 2", scope:"Scope 1" },
  { id:"EF-003", category:"Petrol saloon car",    ef:"2.311", adj:"+18%", source:"DEFRA 2024", tier:"Tier 2", scope:"Scope 1" },
  { id:"EF-004", category:"Petrol SUV",           ef:"2.311", adj:"+18%", source:"DEFRA 2024", tier:"Tier 2", scope:"Scope 1" },
  { id:"EF-005", category:"Diesel 4WD / pickup",  ef:"2.640", adj:"+18%", source:"DEFRA 2024", tier:"Tier 2", scope:"Scope 1" },
  { id:"EF-006", category:"Petrol motorbike",     ef:"2.296", adj:"+18%", source:"DEFRA 2024", tier:"Tier 2", scope:"Scope 1" },
  { id:"EF-007", category:"EV grid charging",     ef:"0.392 /kWh", adj:"—",   source:"KETRACO 2024", tier:"Tier 1", scope:"Scope 1" },
  { id:"EF-008", category:"Short-haul flight",    ef:"0.300 /pkm", adj:"×RFI 1.9", source:"DEFRA 2024", tier:"Tier 2", scope:"Scope 3" },
  { id:"EF-009", category:"Long-haul economy",    ef:"0.370 /pkm", adj:"×RFI 1.9", source:"DEFRA 2024", tier:"Tier 2", scope:"Scope 3" },
  { id:"EF-010", category:"Commute — matatu",     ef:"0.089 /pkm", adj:"—",   source:"Derived Kenya", tier:"Tier 1", scope:"Scope 3" },
];

export const RECOMMENDATIONS = [
  { rank:1, title:"EV fleet transition — heavy vehicles first",       saving:"−620 tCO₂e/yr", cost:"KSh 12,400/t" },
  { rank:2, title:"Remote work policy — 2 days/week",                 saving:"−280 tCO₂e/yr", cost:"KSh 8,200/t"  },
  { rank:3, title:"Route optimisation — Nairobi CBD AI routing",      saving:"−190 tCO₂e/yr", cost:"KSh 6,800/t"  },
  { rank:4, title:"Video-first travel — replace short-haul air",      saving:"−145 tCO₂e/yr", cost:"KSh 5,100/t"  },
  { rank:5, title:"Motorcycle fleet switch to CNG",                   saving:"−88 tCO₂e/yr",  cost:"KSh 4,400/t"  },
];

export const NDC_TRAJECTORY = [
  { year:"FY21", actual:242, ndc:238 }, { year:"FY22", actual:235, ndc:230 },
  { year:"FY23", actual:228, ndc:220 }, { year:"FY24", actual:222, ndc:210 },
  { year:"FY25", actual:218, ndc:200 }, { year:"FY26", actual:null, ndc:192 },
  { year:"FY27", actual:null, ndc:183 }, { year:"FY28", actual:null, ndc:175 },
  { year:"FY30", actual:null, ndc:165 },
];

export const COUNTY_DATA = [
  { county:"Nairobi",  pct:38, val:"82.8K" }, { county:"Mombasa",  pct:14, val:"30.5K" },
  { county:"Kisumu",   pct:9,  val:"19.6K" }, { county:"Nakuru",   pct:8,  val:"17.4K" },
  { county:"Eldoret",  pct:6,  val:"13.1K" }, { county:"Other 42", pct:25, val:"54.6K" },
];
