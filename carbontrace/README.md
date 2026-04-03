# CarbonTrace Kenya 🌿
### AI Transport Emission Disclosure & Reporting Platform
**EPRA Hackathon 2026 · Challenge 2 · Team EmitIQ**

---

## Quick start

```bash
npm install
npm run dev        # http://localhost:5173
```

## Production build

```bash
npm run build      # Output in dist/
npm run preview    # Preview production build
```

## Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite 8 |
| UI components | Flowbite React + Tailwind CSS 3 |
| Charts | Recharts |
| State | React Context |
| Fonts | DM Sans + JetBrains Mono |

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Overview | `/` | KPI dashboard, trend charts, NSE company table |
| Data Ingestion | Sidebar | LayoutLM extraction queue, file status, schema mapping |
| Reconciliation | Sidebar | Isolation Forest anomaly flags, GPS cross-validation |
| GHG Calculator | Sidebar | Scope breakdown, EF register, intensity trend |
| Disclosure Report | Sidebar | Methodology accordion, AI recommendations, PDF/XBRL downloads |
| EPRA Analytics | Sidebar | NDC trajectory, league table, live policy simulation |

## GHG methodology calibration

- **EF source**: DEFRA 2024 Mobile Combustion Factors
- **Kenya road adjustment**: +18% (NTSA fleet data)
- **EV grid EF**: 0.392 kgCO₂e/kWh (KETRACO/EPRA 2024)
- **GWP**: IPCC AR6 100-year (CO₂=1, CH₄=27.9, N₂O=273)
- **Uncertainty**: PyMC Bayesian Monte Carlo ±4.8% (95% CI)
- **Report format**: IFRS S2 XBRL + GRI 305 + NSE ESG Guidance 2021

## Team EmitIQ

| Member | Institution | Role |
|--------|-------------|------|
| Timothy Gitau Muchiri | Co-operative University of Kenya | Team Lead & Backend AI |
| Joanlynn Wambere | Independent Researcher | Cybersecurity & Privacy |
| Collins Njuguna Ndung'u | USIU | Full-Stack & AI Integration |
| Maxwell Gitahi | USIU | Infrastructure & ML |
| Erick Makori Neko | Co-operative University of Kenya | Frontend & UX |
