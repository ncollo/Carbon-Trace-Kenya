# CarbonTrace Kenya — Full Stack Application
### EPRA Hackathon 2026 · Challenge 2 · Team EmitIQ

---

## Prerequisites (install once)

| Software | Where to get | Required version |
|----------|-------------|-----------------|
| Python   | https://python.org/downloads | 3.12 (you have this) |
| Node.js  | https://nodejs.org | 18 LTS or newer |

During Python install — tick **"Add Python to PATH"**

---

## Run the app — open two Command Prompt windows

### Window 1 — Backend (start this FIRST)

```
cd carbontrace-backend
start.bat
```

Wait for: `API running at: http://localhost:8000`

### Window 2 — Frontend

```
cd carbontrace
start.bat
```

Open browser at: **http://localhost:5173**

---

## Folder layout

```
START_HERE.md
carbontrace\           React 18 + Vite + Flowbite + Recharts
carbontrace-backend\   FastAPI + SQLite + Isolation Forest
dataset\
  csv\                 20 CSV files, 12,657 records
```

---

## Troubleshooting

**"python is not recognized"**
  Python is not on PATH. Re-install from python.org and tick "Add Python to PATH"

**"npm is not recognized"**
  Node.js is not installed. Download from nodejs.org (LTS version)

**"Address already in use" on port 8000**
  Something is already on port 8000. In Task Manager end any python.exe process
  or change the port in start.bat: replace 8000 with 8001 in BOTH start.bat AND
  carbontrace\src\api\client.js

**Frontend shows "Backend unreachable"**
  Start the backend (Window 1) before the frontend (Window 2)
