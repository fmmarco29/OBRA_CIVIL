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
