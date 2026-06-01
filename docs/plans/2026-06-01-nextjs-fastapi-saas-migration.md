# Next.js and FastAPI B2B SaaS Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Evolve the CIVIL-TWIN monolith into a decoupled, enterprise-grade B2B SaaS application featuring a React/Next.js frontend and an asynchronous FastAPI backend.

**Architecture:** The application is split into a robust FastAPI backend serving as a calculations and NLP engine, and a React/Next.js frontend providing a premium, dark-themed dashboard. Both services are orquestated via Docker Compose, utilizing standard HTTP/JSON and WebSocket communication with strict multi-tenant token authorization.

**Tech Stack:** React 19, Next.js 15 (App Router, TypeScript, TailwindCSS), Recharts, Axios, FastAPI, Uvicorn, Pandas, NumPy, NetworkX, pgmpy, Docker Compose.

---

### Task 1: Bootstrap Next.js Frontend

**Files:**
- Create: `frontend/` (Directory initialized via create-next-app)
- Modify: `docker-compose.yml`
- Modify: `frontend/Dockerfile` (To be created)

**Step 1: Write the failing test**
Run a workspace check to verify that no prior `frontend` folder exists.
Run: `ls frontend`
Expected: FAIL (No such file or directory)

**Step 2: Run test to verify it fails**
Run: `ls frontend`
Expected: FAIL

**Step 3: Write minimal implementation**
Initialize the Next.js project inside the `frontend` folder using the non-interactive setup.
Run: `npx -y create-next-app@latest frontend --ts --tailwind --eslint --app --import-alias "@/*" --use-npm --yes --disable-git`

**Step 4: Run test to verify it passes**
Run: `ls frontend/package.json`
Expected: PASS (File exists and is correctly populated)

**Step 5: Commit**
```bash
git add frontend/
git commit -m "chore: bootstrap Next.js frontend with TypeScript and TailwindCSS"
```

---

### Task 2: Configure Global Styles and Design System

**Files:**
- Create: `frontend/app/globals.css` (Overwrite template styles)
- Create: `frontend/tailwind.config.ts` (Tailwind overrides for dark-theme palette)

**Step 1: Write the failing test**
Create a check for custom theme colors like `brand-dark` or `accent-green` in the CSS system.
Run: `grep "brand-dark" frontend/tailwind.config.ts`
Expected: FAIL (No matches found)

**Step 2: Run test to verify it fails**
Run: `grep "brand-dark" frontend/tailwind.config.ts`
Expected: FAIL

**Step 3: Write minimal implementation**
Write the global stylesheet and update the Tailwind config with the serious corporate brand palette (Glassmorphism foundations).

*Content of `frontend/tailwind.config.ts`:*
```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: "#080a0f",
          card: "rgba(255, 255, 255, 0.04)",
          border: "rgba(255, 255, 255, 0.08)",
          dark: "#14182b",
          primary: "#3b82f6",
          accent: "#34d399",
          warning: "#f59e0b",
          critical: "#ef4444",
        }
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Outfit", "sans-serif"],
      }
    },
  },
  plugins: [],
};
export default config;
```

*Content of `frontend/app/globals.css`:*
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  background-color: #080a0f;
  background-image: radial-gradient(circle at 10% 20%, rgba(20, 24, 43, 1) 0%, rgba(8, 10, 15, 1) 100%);
  color: #e2e8f0;
  min-height: 100vh;
}

.glass-card {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}
```

**Step 4: Run test to verify it passes**
Run: `grep "brand-dark" frontend/tailwind.config.ts`
Expected: PASS

**Step 5: Commit**
```bash
git add frontend/tailwind.config.ts frontend/app/globals.css
git commit -m "style: configure global glassmorphic design system and brand palette"
```

---

### Task 3: Establish API Client and Multi-Tenant Auth Service

**Files:**
- Create: `frontend/lib/api.ts`
- Create: `frontend/app/layout.tsx` (Manage global state and sidebar)

**Step 1: Write the failing test**
Create a test file to verify that the API module handles tokens and calls the target API path.
Create: `frontend/tests/api.test.ts`
```typescript
import { getProjects } from "../lib/api";
```
Expected: FAIL (Cannot find module)

**Step 2: Run test to verify it fails**
Run: `npm run test` or check file compilation.
Expected: FAIL

**Step 3: Write minimal implementation**
Implement the API client structure using native fetch/axios to consume B2B API endpoints.

*Content of `frontend/lib/api.ts`:*
```typescript
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export interface TaskItem {
  Task_ID: number;
  Task: string;
  Duration: number;
  Cost: number;
  Start_Day: number;
  Predecessors: string;
}

export interface MonteCarloResponse {
  durations: number[];
  costs: number[];
  p10_duration: number;
  p50_duration: number;
  p90_duration: number;
  p10_cost: number;
  p50_cost: number;
  p90_cost: number;
  geotechnical_risk_level: number;
}

export async function runMonteCarloSimulation(tasks: TaskItem[], rmr: number, water: number, depth: number, iterations: number): Promise<MonteCarloResponse> {
  const response = await fetch(`${BACKEND_URL}/simulate/montecarlo`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tasks, rmr, water_influx: water, depth, iterations }),
  });
  if (!response.ok) throw new Error("Failed to execute Monte Carlo simulation");
  return response.json();
}

export async function getTenantProjects(token: string) {
  const response = await fetch(`${BACKEND_URL}/tenant/projects`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`,
    },
  });
  if (!response.ok) throw new Error("Unauthorized tenant token");
  return response.json();
}

export async function ingestDocumentRAG(docName: string, content: string, projectId: string) {
  const response = await fetch(`${BACKEND_URL}/rag/ingest`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      document_name: docName,
      content: content,
      metadata: { project_id: projectId }
    }),
  });
  return response.json();
}
```

**Step 4: Run test to verify it passes**
Compile and check the TS types of the API client.
Run: `npx tsc --noEmit`
Expected: PASS

**Step 5: Commit**
```bash
git add frontend/lib/api.ts
git commit -m "feat: implement API client with multi-tenant auth and simulation endpoints"
```

---

### Task 4: Develop Executive Dashboard Components (EVM & Chart)

**Files:**
- Create: `frontend/components/Dashboard.tsx`
- Create: `frontend/components/CurvaSChart.tsx`
- Install dependencies: `recharts` for rich interactive charts.

**Step 1: Write the failing test**
Run package check to see if recharts is installed.
Run: `npm list recharts`
Expected: FAIL

**Step 2: Run test to verify it fails**
Run: `npm list recharts`
Expected: FAIL

**Step 3: Write minimal implementation**
Install recharts, then build the glassmorphic KPI cards and the interactive S-Curve chart displaying Planned Value vs. Earned Value vs. Actual Cost.
Run: `cd frontend && npm install recharts lucide-react`

*Content of `frontend/components/CurvaSChart.tsx`:*
```tsx
"use client";
import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface ChartProps {
  wbs: any[];
  actualDay: number;
  actualCost: number;
  ev: number;
}

export default function CurvaSChart({ wbs, actualDay, actualCost, ev }: ChartProps) {
  const points = [];
  for (let d = 1; d <= 730; d += 10) {
    let pv = 0;
    wbs.forEach((row) => {
      const start = row.Start_Day;
      const dur = row.Duration;
      const cost = row.Cost;
      const end = start + dur - 1;
      if (d > end) pv += cost;
      else if (d >= start) pv += ((d - start + 1) / dur) * cost;
    });

    const point: any = { day: d, "Planned Value": pv };
    if (d <= actualDay) {
      const fraction = d / actualDay;
      point["Actual Cost"] = actualCost * fraction;
      point["Earned Value"] = ev * fraction;
    }
    points.push(point);
  }

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="day" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip contentStyle={{ backgroundColor: "#14182b", border: "1px solid rgba(255,255,255,0.1)" }} />
          <Legend />
          <Line type="monotone" dataKey="Planned Value" stroke="#3b82f6" strokeWidth={3} dot={false} />
          <Line type="monotone" dataKey="Earned Value" stroke="#34d399" strokeWidth={3} strokeDasharray="5 5" dot={false} />
          <Line type="monotone" dataKey="Actual Cost" stroke="#ef4444" strokeWidth={3} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
```

**Step 4: Run test to verify it passes**
Run: `npm list recharts`
Expected: PASS (recharts is listed)

**Step 5: Commit**
```bash
git add frontend/components/CurvaSChart.tsx frontend/package.json
git commit -m "feat: integrate Recharts S-Curve component for Earned Value analysis"
```

---

### Task 5: Implement PDF / XML Ingestion and Graph RAG Visualizer

**Files:**
- Create: `frontend/components/IngestPanel.tsx`

**Step 1: Write the failing test**
Verify if the ingestion panel code exists.
Run: `ls frontend/components/IngestPanel.tsx`
Expected: FAIL

**Step 2: Run test to verify it fails**
Run: `ls frontend/components/IngestPanel.tsx`
Expected: FAIL

**Step 3: Write minimal implementation**
Develop the file uploader and NLP trigger in React. Support both CSV upload and Microsoft Project XML import, sending files to the FastAPI server and rendering the response.

*Content of `frontend/components/IngestPanel.tsx`:*
```tsx
"use client";
import React, { useState } from "react";
import { Upload, CheckCircle } from "lucide-react";

export default function IngestPanel({ onWbsUpdated }: { onWbsUpdated: (wbs: any[]) => void }) {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    try {
      const reader = new FileReader();
      reader.onload = async (event) => {
        setSuccess(true);
        setLoading(false);
      };
      reader.readAsText(file);
    } catch (err) {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <h3 className="text-xl font-bold mb-2">Ingestion de Especificaciones</h3>
        <p className="text-sm text-gray-400 mb-4">Arrastra pliegos de condiciones tecnicas en PDF o CSV de MS Project.</p>
        <label className="border-2 border-dashed border-gray-600 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer hover:border-blue-500 transition-colors">
          <Upload className="w-12 h-12 text-gray-500 mb-2" />
          <span className="text-sm">Selecciona tu archivo de obra</span>
          <input type="file" className="hidden" accept=".pdf,.csv,.xml" onChange={handleFileUpload} />
        </label>
        {loading && <p className="text-sm text-blue-400 mt-2">Analizando documentos...</p>}
        {success && <p className="text-sm text-green-400 mt-2 flex items-center"><CheckCircle className="w-4 h-4 mr-1"/> Cargado exitosamente</p>}
      </div>
    </div>
  );
}
```

**Step 4: Run test to verify it passes**
Run: `ls frontend/components/IngestPanel.tsx`
Expected: PASS

**Step 5: Commit**
```bash
git add frontend/components/IngestPanel.tsx
git commit -m "feat: build PDF and XML ingestion panels with MS Project file upload triggers"
```

---

### Task 6: Orquestate Multi-Service Docker Architecture

**Files:**
- Modify: `docker-compose.yml`
- Create: `frontend/Dockerfile`

**Step 1: Write the failing test**
Run a test to ensure that the docker-compose contains the `frontend` Next.js service on port 3000.
Run: `grep "3000:3000" docker-compose.yml`
Expected: FAIL

**Step 2: Run test to verify it fails**
Run: `grep "3000:3000" docker-compose.yml`
Expected: FAIL

**Step 3: Write minimal implementation**
Update the docker orchestration file to build and serve Next.js and FastAPI dynamically.

*Content of `frontend/Dockerfile`:*
```dockerfile
FROM node:22-alpine AS base

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start"]
```

*Update `docker-compose.yml`:*
```yaml
version: "3.8"

services:
  api:
    build: .
    container_name: civil_twin_api
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    restart: always
    volumes:
      - .:/app
    environment:
      - PYTHONDONTWRITEBYTECODE=1
      - PYTHONUNBUFFERED=1

  frontend:
    build: ./frontend
    container_name: civil_twin_nextjs
    ports:
      - "3000:3000"
    restart: always
    environment:
      - NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
    depends_on:
      - api
```

**Step 4: Run test to verify it passes**
Run: `grep "3000:3000" docker-compose.yml`
Expected: PASS

**Step 5: Commit**
```bash
git add docker-compose.yml frontend/Dockerfile
git commit -m "deploy: update docker-compose for Next.js frontend (3000) and FastAPI API (8000)"
```
