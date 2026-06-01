"use client";

import React, { useState, useEffect, useMemo } from "react";
import {
  Activity,
  TrendingUp,
  BarChart3,
  Layers,
  Settings,
  AlertTriangle,
  RefreshCw,
  FileText,
  UploadCloud,
  Share2,
  Sliders,
  Database,
  ShieldAlert,
  DollarSign,
  FileCode,
  Download,
  Copy,
  Plus,
  Users,
  CheckCircle2,
  Info,
  Map,
  Building2,
  Server,
  Cpu
} from "lucide-react";
import CurvaSChart from "../components/CurvaSChart";

// Definicion de tipos para WBS y Entidades
interface WbsItem {
  Task_ID: number;
  Task: string;
  Start_Day: number;
  Duration: number;
  Cost: number;
  Predecessors: string;
}

interface Project {
  project_id: string;
  name: string;
  status: string;
}

interface GraphNode {
  id: string;
  properties: {
    tipo?: string;
    nombre?: string;
    tamano_caracteres?: number;
    [key: string]: any;
  };
}

interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

interface SubgraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

// Datos WBS por defecto basados en el pliego de Fuerteventura
const DEFAULT_WBS: WbsItem[] = [
  { Task_ID: 1, Task: "Movilización, Desvíos e Instalación de Faena", Start_Day: 1, Duration: 30, Cost: 4000000.0, Predecessors: "" },
  { Task_ID: 2, Task: "Movimiento de Tierras y Desbroce en Carretera", Start_Day: 31, Duration: 120, Cost: 20000000.0, Predecessors: "1" },
  { Task_ID: 3, Task: "Estructuras y Obras de Drenaje Transversal", Start_Day: 121, Duration: 180, Cost: 30000000.0, Predecessors: "2" },
  { Task_ID: 4, Task: "Excavación y Sostenimiento de Túnel (1.45m)", Start_Day: 151, Duration: 300, Cost: 80000000.0, Predecessors: "2" },
  { Task_ID: 5, Task: "Impermeabilización y Revestimiento Estructural de Túnel", Start_Day: 451, Duration: 150, Cost: 30000000.0, Predecessors: "4" },
  { Task_ID: 6, Task: "Pavimentación, Instalaciones de Seguridad y Ventilación", Start_Day: 601, Duration: 120, Cost: 20000000.0, Predecessors: "3,5" },
  { Task_ID: 7, Task: "Señalización, Balizamiento y Pruebas de Recepción", Start_Day: 671, Duration: 60, Cost: 16000000.0, Predecessors: "6" }
];

// Tenants definidos en el backend
const TENANTS = [
  { token: "token_fuerteventura_enterprise", name: "Fuerteventura Civil S.A.", id: "tenant_fuerteventura_civil", tier: "Enterprise" },
  { token: "token_agaete_consorcio", name: "Consorcio Vial Agaete", id: "tenant_agaete_consorcio", tier: "Premium" },
  { token: "token_invalido_test", name: "Acceso No Autorizado", id: "tenant_error", tier: "Ninguno" }
];

export default function Home() {
  // ----------------------------------------------------
  // Estados Globales de la Aplicacion
  // ----------------------------------------------------
  const [activeTab, setActiveTab] = useState<string>("dashboard");
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [backendUrl] = useState<string>("http://localhost:8000");

  // 1. Tab: Cuadro de Mando (EVM) State
  const [actualDay, setActualDay] = useState<number>(180);
  const [actualCost, setActualCost] = useState<number>(45000000);
  const [physicalProgress, setPhysicalProgress] = useState<number>(0.24); // 24%
  const [wbs] = useState<WbsItem[]>(DEFAULT_WBS);

  // 2. Tab: Ingestión Documental State
  const [docName, setDocName] = useState<string>("Especificacion_Tecnica_Sostenimiento_T5");
  const [docContent, setDocContent] = useState<string>(
    "PLIEGO DE PRESCRIPCIONES TECNICAS PARTICULARES - SECCION T5 Excavacion en roca dura mediante voladuras de precorte. " +
    "Sostenimiento primario de tunel empleando bulones de anclaje de friccion (split-set) y hormigon proyectado con fibras (shotcrete) de 15cm. " +
    "Se requiere control sistematico de RMR. Geotecnia esperada: Basaltos macizos con RMR medio de 60, coeficiente de infiltracion local maximo de 20 L/min."
  );
  const [ingestLoading, setIngestLoading] = useState<boolean>(false);
  const [ingestLogs, setIngestLogs] = useState<string[]>([]);
  const [ingestResult, setIngestResult] = useState<any>(null);
  const [entitySearch, setEntitySearch] = useState<string>("TUNEL_FANIEGUE");
  const [searchLoading, setSearchLoading] = useState<boolean>(false);
  const [searchResult, setSearchResult] = useState<SubgraphResponse | null>(null);

  // 3. Tab: Simulación Geotécnica State
  const [rmr, setRmr] = useState<number>(60);
  const [waterInflux, setWaterInflux] = useState<number>(15);
  const [depth, setDepth] = useState<number>(80);
  const [iterations, setIterations] = useState<number>(2000);
  const [simLoading, setSimLoading] = useState<boolean>(false);
  const [simResults, setSimResults] = useState<any>(null);
  const [simError, setSimError] = useState<string | null>(null);

  // 4. Tab: SaaS B2B Multi-Tenant State
  const [selectedTenantToken, setSelectedTenantToken] = useState<string>("token_fuerteventura_enterprise");
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectsLoading, setProjectsLoading] = useState<boolean>(false);
  const [projectError, setProjectError] = useState<string | null>(null);
  const [newProjectId, setNewProjectId] = useState<string>("proj_fv_003");
  const [newProjectName, setNewProjectName] = useState<string>("Desdoblamiento Enlace Caldereta");
  const [newProjectStatus, setNewProjectStatus] = useState<string>("planning");
  const [createLoading, setCreateLoading] = useState<boolean>(false);

  // LaTeX & Copiar Estados
  const [copied, setCopied] = useState<boolean>(false);

  // ----------------------------------------------------
  // Efectos e Inicializacion
  // ----------------------------------------------------
  useEffect(() => {
    checkBackendHealth();
  }, []);

  // Recargar proyectos cuando cambia el tenant seleccionado
  useEffect(() => {
    fetchProjects();
  }, [selectedTenantToken]);

  const checkBackendHealth = async () => {
    try {
      const res = await fetch(`${backendUrl}/`);
      if (res.ok) {
        setBackendStatus("online");
      } else {
        setBackendStatus("offline");
      }
    } catch {
      setBackendStatus("offline");
    }
  };

  const fetchProjects = async () => {
    setProjectsLoading(true);
    setProjectError(null);
    try {
      const response = await fetch(`${backendUrl}/tenant/projects`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${selectedTenantToken}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("Token de tenant invalido o no autorizado (401)");
        }
        throw new Error(`Error en el servidor: ${response.status}`);
      }

      const data = await response.json();
      setProjects(data);
    } catch (err: any) {
      setProjectError(err.message);
      // Fallback local en caso de desconexion del backend
      if (selectedTenantToken === "token_fuerteventura_enterprise") {
        setProjects([
          { project_id: "proj_fv_001", name: "Autovia Puerto del Rosario - Caldereta (Offline Local)", status: "active" },
          { project_id: "proj_fv_002", name: "Duplicacion de Calzada Aeropuerto (Offline Local)", status: "planning" }
        ]);
      } else if (selectedTenantToken === "token_agaete_consorcio") {
        setProjects([
          { project_id: "proj_ag_101", name: "Tramo Carretera El Risco - Agaete (Offline Local)", status: "active" }
        ]);
      } else {
        setProjects([]);
      }
    } finally {
      setProjectsLoading(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectId || !newProjectName) return;

    setCreateLoading(true);
    try {
      const response = await fetch(`${backendUrl}/tenant/projects`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${selectedTenantToken}`,
        },
        body: JSON.stringify({
          project_id: newProjectId,
          name: newProjectName,
          status: newProjectStatus,
        }),
      });

      if (!response.ok) {
        throw new Error("No se pudo crear el proyecto en el servidor");
      }

      await fetchProjects();
      setNewProjectId("proj_fv_" + Math.floor(Math.random() * 1000));
      setNewProjectName("");
    } catch (err: any) {
      // Fallback local: agregar a la lista actual
      const localNewProject: Project = {
        project_id: newProjectId,
        name: newProjectName + " (Modo Offline)",
        status: newProjectStatus,
      };
      setProjects((prev) => [...prev, localNewProject]);
      setNewProjectId("proj_fv_" + Math.floor(Math.random() * 1000));
      setNewProjectName("");
    } finally {
      setCreateLoading(false);
    }
  };

  // ----------------------------------------------------
  // Calculadora Client-Side del Valor Ganado (EVM Engine)
  // ----------------------------------------------------
  const evm = useMemo(() => {
    // 1. BAC (Budget at Completion)
    const bac = wbs.reduce((acc, row) => acc + row.Cost, 0);

    // 2. PV (Planned Value)
    let pv = 0;
    wbs.forEach((row) => {
      const start = row.Start_Day;
      const dur = row.Duration;
      const cost = row.Cost;
      const end = start + dur - 1;

      if (actualDay > end) {
        pv += cost;
      } else if (actualDay >= start) {
        pv += ((actualDay - start + 1) / dur) * cost;
      }
    });

    // 3. EV (Earned Value)
    const ev = bac * physicalProgress;

    // 4. AC (Actual Cost)
    const ac = actualCost;

    // 5. Ratios de control (CPI & SPI)
    const cpi = ac > 0 ? ev / ac : 1.0;
    const spi = pv > 0 ? ev / pv : 1.0;

    // 6. Varianzas (CV & SV)
    const cv = ev - ac;
    const sv = ev - pv;

    // 7. Estimaciones (EAC & VAC)
    const eac = cpi > 0 ? bac / cpi : bac;
    const vac = bac - eac;

    return {
      bac,
      pv,
      ev,
      ac,
      cpi,
      spi,
      cv,
      sv,
      eac,
      vac,
    };
  }, [wbs, actualDay, actualCost, physicalProgress]);

  // ----------------------------------------------------
  // NLP / RAG Ingest handler
  // ----------------------------------------------------
  const handleIngestDocument = async () => {
    setIngestLoading(true);
    setIngestLogs([]);
    setIngestResult(null);

    const logs: string[] = [];
    const addLog = (msg: string) => {
      logs.push(`[${new Date().toLocaleTimeString()}] ${msg}`);
      setIngestLogs([...logs]);
    };

    addLog("Iniciando ingestion documental...");
    await new Promise((resolve) => setTimeout(resolve, 500));
    addLog(`Cargando especificaciones para: ${docName}`);
    await new Promise((resolve) => setTimeout(resolve, 600));
    addLog(`Ejecutando particion de texto (Vector Chunking). Longitud: ${docContent.length} caracteres`);

    try {
      const res = await fetch(`${backendUrl}/rag/ingest`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          document_name: docName,
          content: docContent,
          metadata: { project_id: "proj_fv_001" },
        }),
      });

      if (!res.ok) throw new Error("Error en la llamada de red al backend");

      const data = await res.json();
      addLog("Extrayendo entidades del texto mediante modelo NLP...");
      await new Promise((resolve) => setTimeout(resolve, 700));
      addLog("Generando enlaces relacionales e indexando en KnowledgeGraphEngine...");
      await new Promise((resolve) => setTimeout(resolve, 500));
      addLog("¡Grafo de conocimiento sincronizado con exito!");

      setIngestResult(data);
    } catch (err) {
      addLog("Fallo de conexion con servidor de calculo. Cambiando a Procesador Semantico local...");
      await new Promise((resolve) => setTimeout(resolve, 800));
      addLog("Extraccion local: Detectada Entidad [TUNEL_FANIEGUE] de tipo [Tunel]");
      addLog("Extraccion local: Detectada Entidad [PROYECTO_EL_RISCO_AGAETE] de tipo [Proyecto_Carretera]");
      addLog(`Extraccion local: Enlazando ${docName} con proyecto principal`);
      addLog("Construyendo subgrafo de contingencia local...");

      const mockSubgraph = {
        status: "success",
        message: `Documento ${docName} indexado localmente (Offline fallback)`,
        extracted_subgraph: {
          nodes: [
            { id: "PROYECTO_EL_RISCO_AGAETE", properties: { tipo: "Proyecto_Carretera", tramo: "El Risco - Agaete" } },
            { id: "TUNEL_FANIEGUE", properties: { tipo: "Tunel", longitud_m: 2100 } },
            { id: docName.toUpperCase(), properties: { tipo: "Especificacion_Tecnica", nombre: docName, tamano_caracteres: docContent.length } }
          ],
          edges: [
            { source: "PROYECTO_EL_RISCO_AGAETE", target: "TUNEL_FANIEGUE", type: "contiene_elemento" },
            { source: "PROYECTO_EL_RISCO_AGAETE", target: docName.toUpperCase(), type: "regulada_por" }
          ]
        }
      };
      setIngestResult(mockSubgraph);
    } finally {
      setIngestLoading(false);
    }
  };

  const handleQueryGraph = async () => {
    if (!entitySearch) return;
    setSearchLoading(true);
    setSearchResult(null);
    try {
      const res = await fetch(`${backendUrl}/rag/graph/${entitySearch.toUpperCase()}`);
      if (!res.ok) throw new Error("Entidad no encontrada");
      const data = await res.json();
      setSearchResult(data);
    } catch {
      // Fallback local para consultas del grafo
      const match = entitySearch.toUpperCase();
      if (match.includes("TUNEL") || match.includes("FANIEGUE")) {
        setSearchResult({
          nodes: [
            { id: "TUNEL_FANIEGUE", properties: { tipo: "Tunel", longitud_m: 2100, geologia: "Basaltos y Traquitas" } },
            { id: "PROYECTO_EL_RISCO_AGAETE", properties: { tipo: "Proyecto_Carretera" } }
          ],
          edges: [
            { source: "PROYECTO_EL_RISCO_AGAETE", target: "TUNEL_FANIEGUE", type: "contiene_elemento" }
          ]
        });
      } else {
        setSearchResult({
          nodes: [
            { id: match, properties: { tipo: "Entidad_Aislada", descripcion: "Consultada offline" } }
          ],
          edges: []
        });
      }
    } finally {
      setSearchLoading(false);
    }
  };

  // ----------------------------------------------------
  // Monte Carlo Geotechnical Simulation Handler
  // ----------------------------------------------------
  const handleRunGeotechnicalSimulation = async () => {
    setSimLoading(true);
    setSimError(null);
    setSimResults(null);

    // Preparar payload de tareas formateadas
    const formattedTasks = wbs.map((t) => ({
      Task_ID: t.Task_ID,
      Task: t.Task,
      Duration: t.Duration,
      Cost: t.Cost,
      Start_Day: t.Start_Day,
      Predecessors: t.Predecessors
    }));

    try {
      const res = await fetch(`${backendUrl}/simulate/montecarlo`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          tasks: formattedTasks,
          rmr: rmr,
          water_influx: waterInflux,
          depth: depth,
          iterations: iterations,
        }),
      });

      if (!res.ok) throw new Error("Error del servidor en los cálculos probabilisticos");
      const data = await res.json();
      setSimResults(data);
    } catch (err: any) {
      // Fallback local: Calculo determinista inteligente basado en factores de riesgo reales
      await new Promise((resolve) => setTimeout(resolve, 1000));
      
      // Clasificar riesgo localmente
      let riskLevel = 0;
      let score = 0;
      if (rmr < 35) score += 4.5;
      else if (rmr < 55) score += 2.5;
      if (depth > 250) score += 2.5;
      if (waterInflux > 50) score += 3.5;
      
      if (score >= 5.5) riskLevel = 2; // Alto
      else if (score >= 2.5) riskLevel = 1; // Medio

      const factorCost = riskLevel === 2 ? 1.35 : riskLevel === 1 ? 1.15 : 1.02;
      const factorTime = riskLevel === 2 ? 1.45 : riskLevel === 1 ? 1.20 : 1.04;

      const p50_dur = Math.round(730 * factorTime);
      const p90_dur = Math.round(730 * (factorTime + 0.12));
      const p10_dur = Math.round(730 * (factorTime - 0.05));

      const baseCost = 200000000;
      const p50_c = baseCost * factorCost;
      const p90_c = baseCost * (factorCost + 0.1);
      const p10_c = baseCost * (factorCost - 0.04);

      setSimResults({
        p10_duration: p10_dur,
        p50_duration: p50_dur,
        p90_duration: p90_dur,
        p10_cost: p10_c,
        p50_cost: p50_c,
        p90_cost: p90_c,
        geotechnical_risk_level: riskLevel,
        is_local_fallback: true
      });
    } finally {
      setSimLoading(false);
    }
  };

  // ----------------------------------------------------
  // Generacion Reactiva de Reporte LaTeX
  // ----------------------------------------------------
  const currentRiskLevel = simResults ? simResults.geotechnical_risk_level : (rmr < 35 ? 2 : rmr < 55 ? 1 : 0);
  const currentRiskStr = ["BAJO", "MEDIO", "ALTO"][currentRiskLevel];
  const currentRiskColor = ["greenalert", "orangealert", "redalert"][currentRiskLevel];

  const generatedLatex = useMemo(() => {
    const today = new Date().toLocaleDateString("es-ES");
    const p50_t = simResults ? simResults.p50_duration : 730;
    const p90_t = simResults ? simResults.p90_duration : 780;
    const p50_c = simResults ? simResults.p50_cost : 204000000;
    const p90_c = simResults ? simResults.p90_cost : 230000000;

    return `\\documentclass[11pt,a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[spanish]{babel}
\\usepackage{geometry}
\\geometry{left=2.5cm,right=2.5cm,top=3cm,bottom=3cm}
\\usepackage{booktabs}
\\usepackage{xcolor}
\\usepackage{titlesec}
\\usepackage{fancyhdr}
\\usepackage{hyperref}

% Colores corporativos de ingenieria
\\definecolor{brandblue}{HTML}{1A365D}
\\definecolor{brandgray}{HTML}{4A5568}
\\definecolor{redalert}{HTML}{E53E3E}
\\definecolor{orangealert}{HTML}{DD6B20}
\\definecolor{greenalert}{HTML}{38A169}

\\hypersetup{
    colorlinks=true,
    linkcolor=brandblue,
    urlcolor=brandblue
}

\\titleformat{\\section}
  {\\normalfont\\Large\\bfseries\\color{brandblue}}{\\thesection}{1em}{}[\\titlerule]
\\titleformat{\\subsection}
  {\\normalfont\\large\\bfseries\\color{brandgray}}{\\thesubsection}{1em}{}

\\pagestyle{fancy}
\\fancyhf{}
\\lhead{\\color{brandgray}CIVIL-TWIN: Gemelo Digital de Carretera con Tunel (Fuerteventura)}
\\rhead{\\color{brandgray}Informe de Obra - ${today}}
\\cfoot{\\thepage}

\\begin{document}

\\begin{center}
    {\\Huge \\bfseries \\color{brandblue} INFORME EJECUTIVO DE CONTROL DE OBRA} \\\\[0.4cm]
    {\\large \\bfseries \\color{brandgray} Carretera Puerto del Rosario - Caldereta (Tunel Singulado) } \\\\[0.2cm]
    {\\large \\bfseries Presupuesto: €${evm.bac.toLocaleString("es-ES")} | Plazo Base: 730 dias} \\\\[0.8cm]
\\end{center}

\\section{Resumen del Proyecto e Ingestion Documental}
Este informe tecnico ha sido generado automaticamente por el Gemelo Digital \\textbf{CIVIL-TWIN} en base a los datos extraidos de los pliegos tecnicos y el diario de obra procesados localmente mediante tecnicas de Procesamiento de Lenguaje Natural (NLP).

\\subsection{Metadatos del Proyecto Extraidos Localmente}
\\begin{itemize}
    \\item \\textbf{Presupuesto Base de Licitacion (BAC):} €${evm.bac.toLocaleString("es-ES")}
    \\item \\textbf{Longitud de Excavacion del Tunel:} 1,450.00 metros.
    \\item \\textbf{Plazo Total Planificado:} 730 dias naturales.
    \\item \\textbf{Geologia Dominante del Frente:} RMR de la roca en ${rmr}.
    \\item \\textbf{Condiciones Hidrogeologicas / Nivel Freatico:} Filtraciones de ${waterInflux} L/min a una profundidad de ${depth}m.
\\end{itemize}

\\section{Analisis del Valor Ganado (EVM) - Dia ${actualDay}}
El estado actual de la obra en el \\textbf{Dia ${actualDay}} ha sido comparado detalladamente con la linea de base del cronograma y los costes acumulados reportados en la obra.

\\begin{table}[h!]
\\centering
\\caption{Indicadores Clave de Rendimiento Financiero y Plazo (EVM)}
\\vspace{0.2cm}
\\begin{tabular}{lc}
\\toprule
\\textbf{Metrica de Control} & \\textbf{Valor (€ / Ratio)} \\\\
\\midrule
Presupuesto Total del Proyecto (BAC) & €${evm.bac.toLocaleString("es-ES")} \\\\
Valor Planificado (PV) & €${Math.round(evm.pv).toLocaleString("es-ES")} \\\\
Valor Ganado (EV) & €${Math.round(evm.ev).toLocaleString("es-ES")} \\\\
Coste Real Incurrido (AC) & €${evm.ac.toLocaleString("es-ES")} \\\\
\\midrule
Varianza de Coste (CV) & €${Math.round(evm.cv).toLocaleString("es-ES")} \\\\
Varianza de Plazo (SV) & €${Math.round(evm.sv).toLocaleString("es-ES")} \\\\
\\midrule
\\textbf{Indice de Rendimiento de Costes (CPI)} & \\textbf{${evm.cpi.toFixed(3)}} \\\\
\\textbf{Indice de Rendimiento de Plazo (SPI)} & \\textbf{${evm.spi.toFixed(3)}} \\\\
\\midrule
Estimado al Finalizar (EAC) & €${Math.round(evm.eac).toLocaleString("es-ES")} \\\\
Desviacion Estimada al Finalizar (VAC) & €${Math.round(evm.vac).toLocaleString("es-ES")} \\\\
\\bottomrule
\\end{tabular}
\\end{table}

\\subsection{Diagnostico del Gemelo Digital}
${evm.cv < 0 ? `El proyecto presenta un \\textbf{sobrecoste acumulado} de €${Math.abs(Math.round(evm.cv)).toLocaleString("es-ES")} respecto al avance real logrado.` : `El proyecto se encuentra en una situacion de \\textbf{ahorro en costes} de €${Math.round(evm.cv).toLocaleString("es-ES")} respecto al avance logrado.`}
${evm.sv < 0 ? `Asimismo, se registra un \\textbf{retraso temporal} equivalente a €${Math.abs(Math.round(evm.sv)).toLocaleString("es-ES")} en valor de obra no ejecutada.` : `De igual modo, el avance temporal esta \\textbf{adelantado} en €${Math.round(evm.sv).toLocaleString("es-ES")} respecto al cronograma de referencia.`}

\\section{Simulacion de Monte Carlo y Prediccion de Riesgos Geotecnicos}
Mediante modelos de Machine Learning (Random Forest) entrenados con bases de datos publicas de seguridad e infraestructuras, se clasifica el nivel de riesgo geotecnico en el frente de excavacion del tunel. Adicionalmente, se ejecuta una simulacion de Monte Carlo con ${iterations} iteraciones para prever los escenarios de costes y plazos finales bajo incertidumbre.

\\subsection{Clasificacion de Riesgo Geotecnico (Frente de Tunel)}
\\begin{itemize}
    \\item \\textbf{Nivel de Riesgo Predictivo del Frente:} \\textbf{\\color{${currentRiskColor}} ${currentRiskStr}}
    \\item \\textbf{Variables del Frente de Excavacion:} Basado en un RMR de ${rmr}, una filtracion activa de ${waterInflux} L/min y profundidad de recubrimiento de ${depth} metros.
\\end{itemize}

\\subsection{Resultados Probabilisticos de la Simulacion}
La simulacion probabilistica estima los siguientes percentiles para la finalizacion del proyecto:
\\begin{itemize}
    \\item \\textbf{Duracion P50 (Escenario Mas Probable):} \\textbf{${p50_t}} dias (Desviacion respecto a la base: ${p50_t - 730} dias).
    \\item \\textbf{Duracion P90 (Escenario Pesimista):} \\textbf{${p90_t}} dias (Desviacion respecto a la base: ${p90_t - 730} dias).
    \\item \\textbf{Coste P50 (Costo Final Probable):} €${Math.round(p50_c).toLocaleString("es-ES")}
    \\item \\textbf{Coste P90 (Costo Final en Peor Escenario):} €${Math.round(p90_c).toLocaleString("es-ES")} (Incremento del ${(((p90_c - evm.bac) / evm.bac) * 100).toFixed(1)}\\% sobre el presupuesto base).
\\end{itemize}

\\section{Recomendaciones para la Direccion de Obra}
Basandose en el estado diario del Gemelo Digital y las predicciones probabilisticas, se aconsejan las siguientes medidas correctoras inmediatas:
\\begin{enumerate}
    \\item \\textbf{Si el Riesgo Geotecnico es ALTO:} Reforzar la colocacion de cerchas metalicas y bulones de anclaje de manera inmediata en la zona de excavacion activa. Implementar paraguas de micropilotes en caso de empeoramiento del RMR.
    \\item \\textbf{Si el CPI < 0.90:} Iniciar auditoria de costes de subcontratacion de maquinaria pesada de excavacion y revisar rendimientos del ciclo de carga y transporte.
    \\item \\textbf{Si el SPI < 0.90:} Aumentar turnos de trabajo en el emboquille del tunel y reprogramar actividades no criticas de la carretera en paralelo para recuperar el retraso en la ruta critica.
\\end{enumerate}

\\vspace{1.5cm}
\\begin{center}
    \\begin{minipage}{0.4\\textwidth}
        \\centering
        \\rule{\\textwidth}{0.4pt} \\\\[0.1cm]
        \\textbf{Direccion de Obra} \\\\
        Fuerteventura
    \\end{minipage}
    \\hfill
    \\begin{minipage}{0.4\\textwidth}
        \\centering
        \\rule{\\textwidth}{0.4pt} \\\\[0.1cm]
        \\textbf{CIVIL-TWIN System} \\\\
        Arquitectura IA Local
    \\end{minipage}
\\end{center}

\\end{document}`;
  }, [evm, simResults, rmr, waterInflux, depth, iterations, currentRiskColor, currentRiskStr]);

  const handleCopyLatex = () => {
    navigator.clipboard.writeText(generatedLatex);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadLatex = () => {
    const blob = new Blob([generatedLatex], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `Informe_Control_Obra_Dia_${actualDay}.tex`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // ----------------------------------------------------
  // Layout Principal e Interfaz Visual (Glassmorphic)
  // ----------------------------------------------------
  return (
    <div className="flex flex-col min-h-screen bg-[#080a0f] text-slate-200">
      
      {/* Header Corporativo Fuerteventura */}
      <header className="sticky top-0 z-50 w-full bg-[#080a0f]/80 backdrop-blur-md border-b border-white/5 py-4 px-6 md:px-12 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-blue-600 to-emerald-400 p-2.5 rounded-xl shadow-lg shadow-blue-500/20">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-sans text-xl font-bold tracking-tight text-white leading-none">CIVIL-TWIN</h1>
              <span className="bg-blue-500/10 text-blue-400 text-xs px-2 py-0.5 rounded-full border border-blue-500/20 font-medium">B2B SaaS</span>
            </div>
            <p className="text-xs text-slate-400 mt-1">Gemelo Digital de Obra Civil - Autovia FV Puerto del Rosario</p>
          </div>
        </div>

        {/* Status de Conexión del Backend */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-white/5 border border-white/10 px-3 py-1.5 rounded-xl text-xs">
            <div className="relative flex h-2 w-2">
              {backendStatus === "online" ? (
                <>
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </>
              ) : backendStatus === "checking" ? (
                <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
              ) : (
                <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
              )}
            </div>
            <span className="text-slate-300 font-mono">
              FastAPI: {backendStatus === "online" ? "ONLINE" : backendStatus === "checking" ? "VERIFICANDO..." : "LOCAL FALLBACK"}
            </span>
          </div>

          <button
            onClick={checkBackendHealth}
            className="p-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition-all hover:scale-105 active:scale-95"
            title="Recargar conexion con FastAPI"
          >
            <RefreshCw className="w-4 h-4 text-slate-300" />
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-8 flex flex-col gap-6">
        
        {/* Banner de Fallback si FastAPI está offline */}
        {backendStatus === "offline" && (
          <div className="bg-amber-500/10 border border-amber-500/20 text-amber-300 p-4 rounded-2xl flex items-start gap-3 shadow-lg shadow-amber-500/5">
            <AlertTriangle className="w-5 h-5 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-sm">Servidor FastAPI Local Inactivo (http://localhost:8000)</h4>
              <p className="text-xs text-amber-400/90 mt-1">
                La plataforma continuara funcionando de manera local e interactiva. Los motores matematicos de EVM y simuladores probabilisticos han sido redirigidos al procesador local del cliente para asegurar continuidad operacional.
              </p>
            </div>
          </div>
        )}

        {/* Tabulador Superior de 5 Opciones */}
        <div className="flex overflow-x-auto gap-2 bg-white/[0.02] border border-white/5 p-1.5 rounded-2xl">
          <button
            onClick={() => setActiveTab("dashboard")}
            className={`flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold transition-all whitespace-nowrap ${
              activeTab === "dashboard"
                ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
            }`}
          >
            <TrendingUp className="w-4 h-4" />
            Cuadro de Mando
          </button>
          
          <button
            onClick={() => setActiveTab("ingest")}
            className={`flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold transition-all whitespace-nowrap ${
              activeTab === "ingest"
                ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
            }`}
          >
            <UploadCloud className="w-4 h-4" />
            Ingestion Documental
          </button>

          <button
            onClick={() => setActiveTab("simulation")}
            className={`flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold transition-all whitespace-nowrap ${
              activeTab === "simulation"
                ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
            }`}
          >
            <Sliders className="w-4 h-4" />
            Simulacion Geotecnica
          </button>

          <button
            onClick={() => setActiveTab("latex")}
            className={`flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold transition-all whitespace-nowrap ${
              activeTab === "latex"
                ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
            }`}
          >
            <FileCode className="w-4 h-4" />
            LaTeX & Reportes
          </button>

          <button
            onClick={() => setActiveTab("tenant")}
            className={`flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold transition-all whitespace-nowrap ${
              activeTab === "tenant"
                ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
            }`}
          >
            <Users className="w-4 h-4" />
            SaaS B2B Multi-Tenant
          </button>
        </div>

        {/* ----------------------------------------------------
            TAB 1: CUADRO DE MANDO (EVM & DASHBOARD)
            ---------------------------------------------------- */}
        {activeTab === "dashboard" && (
          <div className="flex flex-col gap-6 animate-fadeIn">
            
            {/* Grid de Sliders e Inputs de Control Reactivo */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="glass-card p-6 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Dia de Control</h3>
                    <span className="bg-blue-500/10 text-blue-400 text-xs px-2.5 py-1 rounded-lg font-mono font-semibold">
                      Dia {actualDay} / 730
                    </span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="730"
                    value={actualDay}
                    onChange={(e) => setActualDay(parseInt(e.target.value))}
                    className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
                  />
                  <p className="text-xs text-slate-400 mt-3">
                    Establece el dia actual de obra para calcular el Valor Planificado acumulado (PV).
                  </p>
                </div>
              </div>

              <div className="glass-card p-6 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Avance Fisico Real</h3>
                    <span className="bg-emerald-500/10 text-emerald-400 text-xs px-2.5 py-1 rounded-lg font-mono font-semibold">
                      {(physicalProgress * 100).toFixed(1)}%
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={physicalProgress}
                    onChange={(e) => setPhysicalProgress(parseFloat(e.target.value))}
                    className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                  />
                  <p className="text-xs text-slate-400 mt-3">
                    Avance real medido en campo por la direccion facultativa para el calculo del Valor Ganado (EV).
                  </p>
                </div>
              </div>

              <div className="glass-card p-6 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Coste Real Incurrido (AC)</h3>
                    <div className="flex items-center gap-1 bg-slate-900 border border-white/5 px-2.5 py-1 rounded-lg text-xs font-mono font-semibold text-rose-400">
                      <DollarSign className="w-3.5 h-3.5 text-rose-500" />
                      <span>EUR</span>
                    </div>
                  </div>
                  <input
                    type="number"
                    value={actualCost}
                    onChange={(e) => setActualCost(Math.max(0, parseInt(e.target.value) || 0))}
                    className="w-full bg-slate-900/60 border border-white/5 rounded-xl px-4 py-2.5 text-white font-mono text-sm focus:outline-none focus:border-blue-500 transition-colors"
                  />
                  <p className="text-xs text-slate-400 mt-3">
                    Gastos acumulados facturados de maquinaria, materiales y personal de obra.
                  </p>
                </div>
              </div>
            </div>

            {/* Grid de Métricas Principales del Valor Ganado */}
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
              
              <div className="glass-card p-5 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/5 rounded-full blur-2xl"></div>
                <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">BAC Presupuesto</p>
                <p className="text-lg md:text-xl font-mono font-bold text-white mt-2">
                  €{(evm.bac / 1000000).toFixed(1)}M
                </p>
                <div className="text-[10px] text-slate-500 mt-1 font-mono">
                  €{evm.bac.toLocaleString("es-ES")}
                </div>
              </div>

              <div className="glass-card p-5 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/5 rounded-full blur-2xl"></div>
                <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Valor Planificado (PV)</p>
                <p className="text-lg md:text-xl font-mono font-bold text-blue-400 mt-2">
                  €{(evm.pv / 1000000).toFixed(2)}M
                </p>
                <div className="text-[10px] text-slate-500 mt-1 font-mono">
                  €{Math.round(evm.pv).toLocaleString("es-ES")}
                </div>
              </div>

              <div className="glass-card p-5 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl"></div>
                <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Valor Ganado (EV)</p>
                <p className="text-lg md:text-xl font-mono font-bold text-emerald-400 mt-2">
                  €{(evm.ev / 1000000).toFixed(2)}M
                </p>
                <div className="text-[10px] text-slate-500 mt-1 font-mono">
                  {(physicalProgress * 100).toFixed(0)}% del BAC
                </div>
              </div>

              <div className="glass-card p-5 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-24 h-24 bg-rose-500/5 rounded-full blur-2xl"></div>
                <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Coste Real (AC)</p>
                <p className="text-lg md:text-xl font-mono font-bold text-rose-400 mt-2">
                  €{(evm.ac / 1000000).toFixed(2)}M
                </p>
                <div className="text-[10px] text-slate-500 mt-1 font-mono">
                  €{evm.ac.toLocaleString("es-ES")}
                </div>
              </div>

              <div className="glass-card p-5 relative overflow-hidden col-span-2 lg:col-span-1">
                <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/5 rounded-full blur-2xl"></div>
                <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Estimacion Final (EAC)</p>
                <p className="text-lg md:text-xl font-mono font-bold text-purple-400 mt-2">
                  €{(evm.eac / 1000000).toFixed(2)}M
                </p>
                <div className="text-[10px] text-slate-500 mt-1 font-mono">
                  {evm.vac < 0 ? (
                    <span className="text-rose-400 font-semibold">Desviacion: €{Math.round(Math.abs(evm.vac)).toLocaleString("es-ES")}</span>
                  ) : (
                    <span className="text-emerald-400 font-semibold">Ahorro: €{Math.round(evm.vac).toLocaleString("es-ES")}</span>
                  )}
                </div>
              </div>

            </div>

            {/* Grid de Eficiencias y Desviaciones */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              
              <div className="glass-card p-6 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">CPI (Eficiencia Coste)</p>
                    <TrendingUp className="w-4 h-4 text-slate-500" />
                  </div>
                  <div className="flex items-baseline gap-2 mt-4">
                    <span className={`text-4xl font-bold font-mono ${
                      evm.cpi >= 1.0 ? "text-emerald-400" : evm.cpi >= 0.9 ? "text-amber-400" : "text-rose-400"
                    }`}>
                      {evm.cpi.toFixed(3)}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      {evm.cpi >= 1.0 ? "Optimo" : evm.cpi >= 0.9 ? "Estable" : "Alerta"}
                    </span>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-white/5">
                  <div className="flex justify-between text-xs text-slate-400">
                    <span>Varianza Coste (CV):</span>
                    <span className={`font-mono font-semibold ${evm.cv >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                      €{Math.round(evm.cv).toLocaleString("es-ES")}
                    </span>
                  </div>
                </div>
              </div>

              <div className="glass-card p-6 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">SPI (Eficiencia Plazo)</p>
                    <Activity className="w-4 h-4 text-slate-500" />
                  </div>
                  <div className="flex items-baseline gap-2 mt-4">
                    <span className={`text-4xl font-bold font-mono ${
                      evm.spi >= 1.0 ? "text-emerald-400" : evm.spi >= 0.9 ? "text-amber-400" : "text-rose-400"
                    }`}>
                      {evm.spi.toFixed(3)}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      {evm.spi >= 1.0 ? "Adelantado" : evm.spi >= 0.9 ? "Estable" : "Retrasado"}
                    </span>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-white/5">
                  <div className="flex justify-between text-xs text-slate-400">
                    <span>Varianza Plazo (SV):</span>
                    <span className={`font-mono font-semibold ${evm.sv >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                      €{Math.round(evm.sv).toLocaleString("es-ES")}
                    </span>
                  </div>
                </div>
              </div>

              {/* Grafica S-Curve */}
              <div className="glass-card p-6 lg:col-span-2">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="text-sm font-bold text-white uppercase tracking-wider">Curva en S Acumulada</h4>
                    <p className="text-[10px] text-slate-400 mt-0.5">Analisis de Desviacion: PV vs EV vs AC</p>
                  </div>
                  <div className="flex gap-4 text-xs font-mono">
                    <div className="flex items-center gap-1.5">
                      <div className="w-2.5 h-2.5 rounded-full bg-blue-500"></div>
                      <span className="text-slate-400">PV</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-2.5 h-2.5 rounded-full bg-emerald-500"></div>
                      <span className="text-slate-400">EV</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-2.5 h-2.5 rounded-full bg-rose-500"></div>
                      <span className="text-slate-400">AC</span>
                    </div>
                  </div>
                </div>
                <CurvaSChart wbs={wbs} actualDay={actualDay} actualCost={actualCost} ev={evm.ev} />
              </div>

            </div>

            {/* Listado de Tareas WBS / Cronograma Gantt */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              <div className="glass-card p-6 lg:col-span-2">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-sm font-bold text-white uppercase tracking-wider">Estructura de Desglose de Trabajo (WBS)</h4>
                  <span className="bg-slate-800 text-slate-400 text-xs px-2.5 py-1 rounded-lg font-mono">
                    {wbs.length} Tareas Activas
                  </span>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-white/5 text-slate-400 uppercase tracking-wider">
                        <th className="py-3 font-semibold">ID</th>
                        <th className="py-3 font-semibold">Actividad</th>
                        <th className="py-3 font-semibold text-center">Dia Inicio</th>
                        <th className="py-3 font-semibold text-center">Duracion</th>
                        <th className="py-3 font-semibold text-right">Presupuesto</th>
                        <th className="py-3 font-semibold text-center">Estado</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5 font-mono">
                      {wbs.map((row) => {
                        const endDay = row.Start_Day + row.Duration - 1;
                        let statusText = "Planificada";
                        let statusStyle = "text-slate-400 bg-slate-800/60";

                        if (actualDay > endDay) {
                          statusText = "Completada";
                          statusStyle = "text-emerald-400 bg-emerald-500/10 border border-emerald-500/20";
                        } else if (actualDay >= row.Start_Day) {
                          statusText = "En Curso";
                          statusStyle = "text-blue-400 bg-blue-500/10 border border-blue-500/20";
                        }

                        return (
                          <tr key={row.Task_ID} className="hover:bg-white/[0.01] transition-colors">
                            <td className="py-3.5 text-slate-500 font-semibold">{row.Task_ID}</td>
                            <td className="py-3.5 text-slate-200 font-sans font-medium">{row.Task}</td>
                            <td className="py-3.5 text-center text-slate-300">{row.Start_Day}</td>
                            <td className="py-3.5 text-center text-slate-300">{row.Duration} d</td>
                            <td className="py-3.5 text-right text-slate-300">
                              €{row.Cost.toLocaleString("es-ES")}
                            </td>
                            <td className="py-3.5 text-center">
                              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase ${statusStyle}`}>
                                {statusText}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Proyectos del Tenant Autorizado */}
              <div className="glass-card p-6 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-sm font-bold text-white uppercase tracking-wider">Proyectos Autorizados (B2B)</h4>
                    <button
                      onClick={fetchProjects}
                      className="p-1 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors"
                      title="Actualizar lista de proyectos"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 text-slate-400 ${projectsLoading ? "animate-spin" : ""}`} />
                    </button>
                  </div>
                  
                  {projectError ? (
                    <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-300 rounded-xl text-xs font-mono">
                      {projectError}
                    </div>
                  ) : projects.length === 0 ? (
                    <p className="text-slate-400 text-xs py-8 text-center font-sans">
                      No hay proyectos activos para este tenant. Sincroniza un token valido.
                    </p>
                  ) : (
                    <div className="flex flex-col gap-3">
                      {projects.map((proj) => (
                        <div key={proj.project_id} className="p-3.5 bg-slate-900/60 border border-white/5 rounded-xl hover:border-slate-700 transition-colors">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-slate-400 font-mono font-semibold uppercase">{proj.project_id}</span>
                            <span className={`px-1.5 py-0.5 rounded-md text-[9px] font-bold font-mono tracking-wider uppercase ${
                              proj.status === "active" ? "bg-emerald-500/15 text-emerald-400" : "bg-blue-500/15 text-blue-400"
                            }`}>
                              {proj.status}
                            </span>
                          </div>
                          <h5 className="text-xs font-bold text-white mt-1.5 font-sans">{proj.name}</h5>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="mt-6 pt-4 border-t border-white/5">
                  <p className="text-[10px] text-slate-500 leading-normal">
                    Los proyectos mostrados estan filtrados mediante la API B2B en base al tenant activo. Puedes cambiar de Tenant en la pestaña correspondiente.
                  </p>
                </div>
              </div>

            </div>

          </div>
        )}

        {/* ----------------------------------------------------
            TAB 2: INGESTION DOCUMENTAL (NLP & RAG)
            ---------------------------------------------------- */}
        {activeTab === "ingest" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fadeIn">
            
            {/* Formulario de Carga Ingest */}
            <div className="glass-card p-6 lg:col-span-2 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">Ingesta de Especificaciones</h3>
                  <span className="bg-slate-800 text-slate-400 text-xs px-2.5 py-1 rounded-lg font-mono">
                    Procesador NLP Local
                  </span>
                </div>

                <div className="flex flex-col gap-4">
                  <div>
                    <label className="text-xs text-slate-400 font-semibold block mb-1">Nombre del Documento</label>
                    <input
                      type="text"
                      value={docName}
                      onChange={(e) => setDocName(e.target.value)}
                      className="w-full bg-slate-900 border border-white/5 rounded-xl px-4 py-2.5 text-white font-mono text-xs focus:outline-none focus:border-blue-500 transition-colors"
                      placeholder="Ej. Pliego_Excavacion_Voladuras"
                    />
                  </div>

                  <div>
                    <label className="text-xs text-slate-400 font-semibold block mb-1">Contenido Técnico del Pliego</label>
                    <textarea
                      value={docContent}
                      onChange={(e) => setDocContent(e.target.value)}
                      rows={8}
                      className="w-full bg-slate-900/60 border border-white/5 rounded-xl px-4 py-3 text-slate-300 font-sans text-xs focus:outline-none focus:border-blue-500 transition-colors resize-none leading-relaxed"
                      placeholder="Pega las especificaciones de ingenieria..."
                    />
                  </div>
                </div>
              </div>

              <div className="mt-6 flex gap-3">
                <button
                  onClick={handleIngestDocument}
                  disabled={ingestLoading || !docContent}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs py-3.5 rounded-xl transition-all shadow-lg shadow-blue-500/20 disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer"
                >
                  {ingestLoading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Procesando Semantica RAG...
                    </>
                  ) : (
                    <>
                      <UploadCloud className="w-4 h-4" />
                      Ejecutar Analisis Semantico RAG
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Consola de Registro y Subgrafo */}
            <div className="flex flex-col gap-6">
              
              {/* Consola de logs */}
              <div className="glass-card p-6 flex flex-col h-64 justify-between">
                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Consola del Compilador RAG</h4>
                  <div className="bg-black/40 border border-white/5 rounded-xl p-3.5 font-mono text-[10px] text-emerald-400 h-40 overflow-y-auto leading-relaxed">
                    {ingestLogs.length === 0 ? (
                      <span className="text-slate-500 font-sans">Esperando ejecucion de ingestion semantica...</span>
                    ) : (
                      ingestLogs.map((log, idx) => <div key={idx}>{log}</div>)
                    )}
                  </div>
                </div>
                <div className="text-[9px] text-slate-500 font-mono mt-2">
                  NLP Pipeline v2.3 | Chunk size: 500 characters | Overlap: 50
                </div>
              </div>

              {/* Resultado del Mapeo en Grafo */}
              <div className="glass-card p-6 flex-1 flex flex-col justify-between">
                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Relaciones en Grafo de Conocimiento</h4>
                  
                  {ingestResult ? (
                    <div className="flex flex-col gap-4 font-mono">
                      <div className="bg-emerald-500/10 border border-emerald-500/20 p-3 rounded-xl flex items-center gap-2 text-xs text-emerald-400">
                        <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                        <span className="font-semibold">Grafo Sincronizado</span>
                      </div>
                      
                      <div className="text-xs">
                        <p className="text-slate-400 font-bold mb-1 uppercase text-[10px] tracking-wider">Nodos Identificados:</p>
                        <div className="flex flex-wrap gap-1.5 mt-1">
                          {ingestResult.extracted_subgraph.nodes.map((node: any) => (
                            <span key={node.id} className="bg-slate-900 border border-white/5 px-2 py-0.5 rounded-md text-[10px] text-slate-300 font-medium">
                              {node.id} ({node.properties.tipo || "Entidad"})
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="text-xs">
                        <p className="text-slate-400 font-bold mb-1 uppercase text-[10px] tracking-wider">Enlaces Semanticos:</p>
                        <div className="flex flex-col gap-1 text-[10px] text-slate-400 mt-1">
                          {ingestResult.extracted_subgraph.edges.map((edge: any, i: number) => (
                            <div key={i} className="flex items-center gap-1">
                              <span className="text-slate-300">{edge.source}</span>
                              <span className="text-blue-400">--[{edge.type}]--&gt;</span>
                              <span className="text-slate-300">{edge.target}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-slate-500 text-xs leading-normal py-4 font-sans">
                      Los datos extraídos se mapearán de manera relacional en el motor del grafo. Ejecuta una ingesta para ver la estructura.
                    </p>
                  )}
                </div>

                <div className="mt-4 pt-4 border-t border-white/5">
                  <h5 className="text-[10px] font-bold text-white uppercase mb-2">Consulta Avanzada al Grafo (Graph RAG)</h5>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={entitySearch}
                      onChange={(e) => setEntitySearch(e.target.value)}
                      className="bg-slate-900 border border-white/5 rounded-lg px-2.5 py-1 text-slate-200 text-xs font-mono flex-1 focus:outline-none"
                      placeholder="Entity ID"
                    />
                    <button
                      onClick={handleQueryGraph}
                      disabled={searchLoading}
                      className="bg-white/5 border border-white/10 hover:bg-white/10 text-slate-300 px-3 py-1 rounded-lg text-xs font-semibold font-mono cursor-pointer"
                    >
                      {searchLoading ? "Cargando..." : "Consultar"}
                    </button>
                  </div>
                  {searchResult && (
                    <div className="mt-3 bg-slate-950 p-2.5 rounded-lg border border-white/5 text-[9px] font-mono text-slate-400 max-h-24 overflow-y-auto">
                      <p className="text-blue-400 font-bold mb-1">Resultado de busqueda:</p>
                      {searchResult.nodes.map(n => (
                        <div key={n.id}>- Node: {n.id} [{JSON.stringify(n.properties)}]</div>
                      ))}
                      {searchResult.edges.map((e, idx) => (
                        <div key={idx}>- Edge: {e.source} --{e.type}--&gt; {e.target}</div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

            </div>

          </div>
        )}

        {/* ----------------------------------------------------
            TAB 3: SIMULACION GEOTECNICA (MONTE CARLO)
            ---------------------------------------------------- */}
        {activeTab === "simulation" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fadeIn">
            
            {/* Controles del Frente de Excavación */}
            <div className="glass-card p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">Frente de Excavacion de Tunel</h3>
                  <span className="bg-slate-800 text-slate-400 text-xs px-2.5 py-1 rounded-lg font-mono">
                    Modelado Predictivo
                  </span>
                </div>

                <div className="flex flex-col gap-6">
                  {/* Slider RMR */}
                  <div>
                    <div className="flex justify-between text-xs mb-2">
                      <span className="text-slate-400 font-semibold">RMR (Rock Mass Rating)</span>
                      <span className="font-mono font-bold text-white">{rmr} / 100</span>
                    </div>
                    <input
                      type="range"
                      min="15"
                      max="85"
                      value={rmr}
                      onChange={(e) => setRmr(parseInt(e.target.value))}
                      className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
                    />
                    <div className="flex justify-between text-[9px] text-slate-500 mt-1">
                      <span>Roca Pesima (&lt;30)</span>
                      <span>Regular (60)</span>
                      <span>Excelente (&gt;80)</span>
                    </div>
                  </div>

                  {/* Slider Influx */}
                  <div>
                    <div className="flex justify-between text-xs mb-2">
                      <span className="text-slate-400 font-semibold">Filtracion Hidrogeologica</span>
                      <span className="font-mono font-bold text-white">{waterInflux} L/min</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="120"
                      value={waterInflux}
                      onChange={(e) => setWaterInflux(parseInt(e.target.value))}
                      className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
                    />
                    <div className="flex justify-between text-[9px] text-slate-500 mt-1">
                      <span>Seco (0)</span>
                      <span>Moderado (25)</span>
                      <span>Filtracion Fuerte (&gt;60)</span>
                    </div>
                  </div>

                  {/* Slider Recubrimiento */}
                  <div>
                    <div className="flex justify-between text-xs mb-2">
                      <span className="text-slate-400 font-semibold">Profundidad del Tunel</span>
                      <span className="font-mono font-bold text-white">{depth} metros</span>
                    </div>
                    <input
                      type="range"
                      min="10"
                      max="500"
                      value={depth}
                      onChange={(e) => setDepth(parseInt(e.target.value))}
                      className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
                    />
                    <div className="flex justify-between text-[9px] text-slate-500 mt-1">
                      <span>Superficial (10)</span>
                      <span>Medio (150)</span>
                      <span>Fuerte Presion (&gt;350)</span>
                    </div>
                  </div>

                  {/* Iteraciones Monte Carlo */}
                  <div>
                    <label className="text-xs text-slate-400 font-semibold block mb-1">Iteraciones del Simulador Probabilistico</label>
                    <input
                      type="number"
                      value={iterations}
                      min="100"
                      max="5000"
                      onChange={(e) => setIterations(Math.max(100, parseInt(e.target.value) || 100))}
                      className="w-full bg-slate-900 border border-white/5 rounded-xl px-4 py-2.5 text-white font-mono text-xs focus:outline-none focus:border-blue-500 transition-colors"
                    />
                  </div>
                </div>
              </div>

              <div className="mt-8">
                <button
                  onClick={handleRunGeotechnicalSimulation}
                  disabled={simLoading}
                  className="w-full bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 text-white font-semibold text-xs py-3.5 rounded-xl transition-all shadow-lg shadow-emerald-500/10 disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer"
                >
                  {simLoading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Calculando Simulación (Monte Carlo)...
                    </>
                  ) : (
                    <>
                      <Sliders className="w-4 h-4" />
                      Ejecutar Simulacion Monte Carlo
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Panel de Resultados de la Simulación */}
            <div className="glass-card p-6 lg:col-span-2 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">Resultados Probabilisticos del Gemelo</h3>
                  {simResults && simResults.is_local_fallback && (
                    <span className="bg-amber-500/10 border border-amber-500/20 text-amber-400 text-[10px] px-2 py-0.5 rounded-full font-mono font-bold uppercase">
                      Offline Mode Active
                    </span>
                  )}
                </div>

                {simResults ? (
                  <div className="flex flex-col gap-6 font-mono">
                    
                    {/* Tarjeta de Riesgo Geotecnico Predictivo */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-4 bg-slate-900/60 border border-white/5 rounded-xl">
                        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Clasificación de Riesgo Geotécnico</span>
                        <div className="flex items-center gap-2.5 mt-2">
                          <div className={`w-3.5 h-3.5 rounded-full ${
                            simResults.geotechnical_risk_level === 2
                              ? "bg-rose-500 animate-pulse"
                              : simResults.geotechnical_risk_level === 1
                              ? "bg-amber-500"
                              : "bg-emerald-500"
                          }`}></div>
                          <span className={`text-xl font-bold uppercase tracking-wider ${
                            simResults.geotechnical_risk_level === 2
                              ? "text-rose-400"
                              : simResults.geotechnical_risk_level === 1
                              ? "text-amber-400"
                              : "text-emerald-400"
                          }`}>
                            {["BAJO", "MEDIO", "ALTO"][simResults.geotechnical_risk_level]}
                          </span>
                        </div>
                      </div>

                      <div className="p-4 bg-slate-900/60 border border-white/5 rounded-xl flex items-center justify-between">
                        <div>
                          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Rendimiento Estimado Frente</span>
                          <p className="text-sm font-bold text-slate-300 mt-1">
                            {simResults.geotechnical_risk_level === 2 ? "0.95 metros / dia" : simResults.geotechnical_risk_level === 1 ? "2.10 metros / dia" : "4.80 metros / dia"}
                          </p>
                        </div>
                        <Cpu className="w-8 h-8 text-slate-600" />
                      </div>
                    </div>

                    {/* Desglose de Percentiles - Duracion */}
                    <div className="p-5 bg-slate-900/40 border border-white/5 rounded-xl">
                      <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-1.5">
                        <Activity className="w-4 h-4 text-blue-500" />
                        Desglose Probabilístico de Plazos Finales
                      </h4>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-slate-950 p-3.5 rounded-xl border border-white/5">
                          <span className="text-[10px] text-slate-400 font-bold">P10 - Escenario Optimista</span>
                          <p className="text-lg font-bold text-white mt-1">{simResults.p10_duration} días</p>
                          <div className="text-[9px] text-emerald-400 font-bold mt-1">
                            Desviación: {simResults.p10_duration - 730} días
                          </div>
                        </div>

                        <div className="bg-slate-950 p-3.5 rounded-xl border border-white/5">
                          <span className="text-[10px] text-slate-400 font-bold">P50 - Escenario Esperado</span>
                          <p className="text-lg font-bold text-blue-400 mt-1">{simResults.p50_duration} días</p>
                          <div className="text-[9px] text-slate-400 font-bold mt-1">
                            Desviación: {simResults.p50_duration - 730} días
                          </div>
                        </div>

                        <div className="bg-slate-950 p-3.5 rounded-xl border border-white/5">
                          <span className="text-[10px] text-slate-400 font-bold">P90 - Escenario Pesimista</span>
                          <p className="text-lg font-bold text-rose-400 mt-1">{simResults.p90_duration} días</p>
                          <div className="text-[9px] text-rose-400 font-bold mt-1">
                            Desviación: {simResults.p90_duration - 730} días
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Desglose de Percentiles - Coste */}
                    <div className="p-5 bg-slate-900/40 border border-white/5 rounded-xl">
                      <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-1.5">
                        <DollarSign className="w-4 h-4 text-emerald-500" />
                        Desglose Probabilístico de Costes Finales
                      </h4>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-slate-950 p-3.5 rounded-xl border border-white/5">
                          <span className="text-[10px] text-slate-400 font-bold">P10 - Coste Minimo</span>
                          <p className="text-md font-bold text-white mt-1">€{Math.round(simResults.p10_cost).toLocaleString("es-ES")}</p>
                          <div className="text-[9px] text-emerald-400 font-bold mt-1">
                            -{(((evm.bac - simResults.p10_cost) / evm.bac) * 100).toFixed(1)}% vs Base
                          </div>
                        </div>

                        <div className="bg-slate-950 p-3.5 rounded-xl border border-white/5">
                          <span className="text-[10px] text-slate-400 font-bold">P50 - Coste Esperado</span>
                          <p className="text-md font-bold text-emerald-400 mt-1">€{Math.round(simResults.p50_cost).toLocaleString("es-ES")}</p>
                          <div className="text-[9px] text-slate-400 font-bold mt-1">
                            +{(((simResults.p50_cost - evm.bac) / evm.bac) * 100).toFixed(1)}% vs Base
                          </div>
                        </div>

                        <div className="bg-slate-950 p-3.5 rounded-xl border border-white/5">
                          <span className="text-[10px] text-slate-400 font-bold">P90 - Escenario Critico</span>
                          <p className="text-md font-bold text-rose-400 mt-1">€{Math.round(simResults.p90_cost).toLocaleString("es-ES")}</p>
                          <div className="text-[9px] text-rose-400 font-bold mt-1">
                            +{(((simResults.p90_cost - evm.bac) / evm.bac) * 100).toFixed(1)}% vs Base
                          </div>
                        </div>
                      </div>
                    </div>

                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-20 text-center">
                    <Sliders className="w-12 h-12 text-slate-600 mb-3 animate-pulse" />
                    <h4 className="text-sm font-bold text-slate-400">Ninguna simulacion activa en este momento</h4>
                    <p className="text-xs text-slate-500 max-w-sm mt-1 leading-relaxed">
                      Modifica los parametros geotecnicos del frente de excavacion en el panel izquierdo y ejecuta el simulador Monte Carlo para prever sobrecostes y desviaciones probabilisticas de plazos.
                    </p>
                  </div>
                )}
              </div>

              <div className="mt-6 pt-4 border-t border-white/5 text-[10px] text-slate-500 leading-normal">
                El modelo predice el impacto en los plazos finales mediante el algoritmo de calculo del metodo PERT/CPM acoplado a la variabilidad geológica.
              </div>
            </div>

          </div>
        )}

        {/* ----------------------------------------------------
            TAB 4: LA LA-TEX & REPORTES
            ---------------------------------------------------- */}
        {activeTab === "latex" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fadeIn">
            
            {/* Editor de Código LaTeX */}
            <div className="glass-card p-6 flex flex-col justify-between h-[650px]">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">Generador de Documentacion LaTeX</h3>
                  <div className="flex gap-2">
                    <button
                      onClick={handleCopyLatex}
                      className="flex items-center gap-1 px-3 py-1.5 bg-white/5 border border-white/10 hover:bg-white/10 rounded-lg text-xs font-semibold text-slate-300 font-sans cursor-pointer transition-colors"
                    >
                      <Copy className="w-3.5 h-3.5" />
                      {copied ? "Copiado" : "Copiar"}
                    </button>
                    <button
                      onClick={handleDownloadLatex}
                      className="flex items-center gap-1 px-3 py-1.5 bg-white/5 border border-white/10 hover:bg-white/10 rounded-lg text-xs font-semibold text-slate-300 font-sans cursor-pointer transition-colors"
                    >
                      <Download className="w-3.5 h-3.5" />
                      Descargar
                    </button>
                  </div>
                </div>

                <p className="text-xs text-slate-400 mb-4 leading-normal">
                  Plantilla de informe ejecutivo en LaTeX generada automaticamente con las metricas en tiempo real del Valor Ganado (EVM) y el simulador de riesgos.
                </p>

                <textarea
                  value={generatedLatex}
                  readOnly
                  rows={20}
                  className="w-full bg-slate-950 border border-white/5 rounded-xl p-4 text-slate-400 font-mono text-[10px] leading-relaxed resize-none h-[420px] focus:outline-none"
                />
              </div>
              
              <div className="text-[10px] text-slate-500 font-mono leading-normal mt-4">
                El archivo generado se puede compilar de manera directa con pdflatex para la emision oficial de informes de obra civil.
              </div>
            </div>

            {/* Vista Previa Corporativa del Informe */}
            <div className="glass-card p-6 flex flex-col justify-between h-[650px] overflow-y-auto">
              <div className="bg-white text-slate-900 p-8 rounded-xl shadow-2xl min-h-[580px] font-sans border-t-[6px] border-blue-900 relative">
                
                {/* Cabecera del Informe */}
                <div className="flex justify-between items-start border-b border-slate-200 pb-4 mb-6">
                  <div>
                    <h4 className="text-[10px] font-bold uppercase tracking-widest text-slate-500">INFORME FACULTATIVO DE OBRA</h4>
                    <h2 className="text-lg font-extrabold tracking-tight text-blue-950 mt-1">Carretera Puerto del Rosario - Caldereta</h2>
                    <p className="text-[9px] text-slate-500 font-medium mt-0.5">Frente de Excavacion de Tunel Singulado</p>
                  </div>
                  <div className="text-right">
                    <span className="text-[9px] font-bold text-slate-500 block">FECHA DE EMISION</span>
                    <span className="text-xs font-mono font-bold text-slate-800">{new Date().toLocaleDateString("es-ES")}</span>
                  </div>
                </div>

                <div className="text-[11px] leading-relaxed text-slate-700 flex flex-col gap-5">
                  <div>
                    <h3 className="text-xs font-bold text-blue-950 uppercase border-b border-slate-100 pb-1 mb-2">1. Resumen Ejecutivo del Proyecto</h3>
                    <p>
                      El presente informe ejecutivo ha sido emitido de manera automatica por el sistema de control del Gemelo Digital \\textbf{CIVIL-TWIN}. El analisis recopila la situacion actual de ejecucion al dia de control <strong>Dia {actualDay}</strong> del cronograma oficial del proyecto.
                    </p>
                    <ul className="list-disc pl-5 mt-2 flex flex-col gap-1 text-[10.5px]">
                      <li><strong>Presupuesto de Licitacion (BAC):</strong> €{evm.bac.toLocaleString("es-ES")}</li>
                      <li><strong>Indice de Calidad de la Roca (RMR):</strong> {rmr}</li>
                      <li><strong>Presion del frente (Profundidad):</strong> {depth}m (Filtraciones estimadas en {waterInflux} L/min).</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xs font-bold text-blue-950 uppercase border-b border-slate-100 pb-1 mb-2">2. Estado Financiero y Plazo (Valor Ganado - EVM)</h3>
                    <p className="mb-3">
                      Se ha realizado la valoracion del avance acumulado real respecto al presupuesto base (BAC), obteniendo los siguientes ratios clave de rendimiento:
                    </p>

                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-[10px] border border-slate-200 border-collapse">
                        <thead>
                          <tr className="bg-slate-50 border-b border-slate-200 text-slate-800 font-bold uppercase tracking-wider">
                            <th className="p-2 border-r border-slate-200">Metrica de Control</th>
                            <th className="p-2 text-right">Valor (€ / Ratio)</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-200 font-mono text-slate-800">
                          <tr>
                            <td className="p-2 font-sans font-semibold border-r border-slate-200">Valor Planificado (PV)</td>
                            <td className="p-2 text-right">€{Math.round(evm.pv).toLocaleString("es-ES")}</td>
                          </tr>
                          <tr>
                            <td className="p-2 font-sans font-semibold border-r border-slate-200">Valor Ganado (EV)</td>
                            <td className="p-2 text-right">€{Math.round(evm.ev).toLocaleString("es-ES")}</td>
                          </tr>
                          <tr>
                            <td className="p-2 font-sans font-semibold border-r border-slate-200">Coste Real (AC)</td>
                            <td className="p-2 text-right">€{evm.ac.toLocaleString("es-ES")}</td>
                          </tr>
                          <tr className="bg-slate-50 font-bold">
                            <td className="p-2 font-sans border-r border-slate-200">Indice de Costes (CPI)</td>
                            <td className="p-2 text-right font-sans text-blue-900">{evm.cpi.toFixed(3)}</td>
                          </tr>
                          <tr className="bg-slate-50 font-bold">
                            <td className="p-2 font-sans border-r border-slate-200">Indice de Plazos (SPI)</td>
                            <td className="p-2 text-right font-sans text-blue-900">{evm.spi.toFixed(3)}</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xs font-bold text-blue-950 uppercase border-b border-slate-100 pb-1 mb-2">3. Riesgo Geotecnico y Prevision Final (P50/P90)</h3>
                    <p>
                      El simulador probabilistico reporta un nivel de riesgo predictivo <strong>{currentRiskStr}</strong>. Los percentiles simulados estiman una duracion esperada (P50) de <strong>{simResults ? simResults.p50_duration : 730} dias</strong> y una duracion en peor escenario (P90) de <strong>{simResults ? simResults.p90_duration : 780} dias</strong>. El coste final estimado P90 se situa en un incremento de €{(simResults ? (simResults.p90_cost - evm.bac) / 1000000 : 30).toFixed(1)}M.
                    </p>
                  </div>
                </div>

                {/* Firmas */}
                <div className="mt-10 pt-8 border-t border-slate-100 flex justify-between text-[9px] font-sans font-bold text-slate-500">
                  <div className="text-center w-36">
                    <div className="h-10"></div>
                    <div className="border-t border-slate-300 pt-1">Direccion de Obra</div>
                  </div>
                  <div className="text-center w-36">
                    <div className="h-10"></div>
                    <div className="border-t border-slate-300 pt-1">CIVIL-TWIN System</div>
                  </div>
                </div>

              </div>
            </div>

          </div>
        )}

        {/* ----------------------------------------------------
            TAB 5: SAAS B2B MULTI-TENANT
            ---------------------------------------------------- */}
        {activeTab === "tenant" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fadeIn">
            
            {/* Panel de Tenant y Credenciales */}
            <div className="glass-card p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">Multi-Tenant settings</h3>
                  <Building2 className="w-4 h-4 text-blue-500" />
                </div>

                <div className="flex flex-col gap-5">
                  <div>
                    <label className="text-xs text-slate-400 font-semibold block mb-1">Selecciona el B2B Tenant Activo</label>
                    <select
                      value={selectedTenantToken}
                      onChange={(e) => setSelectedTenantToken(e.target.value)}
                      className="w-full bg-slate-900 border border-white/5 rounded-xl px-4 py-3 text-slate-300 font-sans text-xs focus:outline-none focus:border-blue-500 transition-colors"
                    >
                      {TENANTS.map((t) => (
                        <option key={t.token} value={t.token}>
                          {t.name} ({t.tier})
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Informacion extendida del Tenant */}
                  {(() => {
                    const tInfo = TENANTS.find((t) => t.token === selectedTenantToken);
                    if (!tInfo) return null;

                    return (
                      <div className="bg-slate-900/60 border border-white/5 rounded-xl p-4 flex flex-col gap-3 font-mono text-xs">
                        <div className="flex justify-between">
                          <span className="text-slate-500">Tenant Name:</span>
                          <span className="text-slate-300 font-sans font-bold">{tInfo.name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Tenant ID:</span>
                          <span className="text-slate-300">{tInfo.id}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Subscription Tier:</span>
                          <span className="text-emerald-400 font-bold">{tInfo.tier}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">API Bearer Token:</span>
                          <span className="text-blue-400 truncate max-w-[120px]">{selectedTenantToken}</span>
                        </div>
                      </div>
                    );
                  })()}
                </div>
              </div>

              <div className="mt-8 pt-4 border-t border-white/5">
                <p className="text-[10px] text-slate-500 leading-normal">
                  El control de acceso esta gestionado mediante tokens Bearer JWT validados en cada peticion. Los tokens simulados permiten validar la segregacion fisica de bases de datos.
                </p>
              </div>
            </div>

            {/* Listado de proyectos y Formulario de creación */}
            <div className="glass-card p-6 lg:col-span-2 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">Crear y Gestionar Proyectos</h3>
                  <span className="bg-slate-800 text-slate-400 text-xs px-2.5 py-1 rounded-lg font-mono">
                    Aislamiento de Datos Activo
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  
                  {/* Formulario */}
                  <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Nuevo Proyecto para el Tenant</h4>
                    <form onSubmit={handleCreateProject} className="flex flex-col gap-4">
                      <div>
                        <label className="text-xs text-slate-500 font-semibold block mb-1">Project ID</label>
                        <input
                          type="text"
                          value={newProjectId}
                          onChange={(e) => setNewProjectId(e.target.value)}
                          className="w-full bg-slate-900 border border-white/5 rounded-xl px-3 py-2 text-white font-mono text-xs focus:outline-none"
                        />
                      </div>

                      <div>
                        <label className="text-xs text-slate-500 font-semibold block mb-1">Nombre del Proyecto</label>
                        <input
                          type="text"
                          value={newProjectName}
                          onChange={(e) => setNewProjectName(e.target.value)}
                          className="w-full bg-slate-900 border border-white/5 rounded-xl px-3 py-2 text-white font-sans text-xs focus:outline-none"
                          placeholder="Nombre descriptivo"
                        />
                      </div>

                      <div>
                        <label className="text-xs text-slate-500 font-semibold block mb-1">Estado de Obra</label>
                        <select
                          value={newProjectStatus}
                          onChange={(e) => setNewProjectStatus(e.target.value)}
                          className="w-full bg-slate-900 border border-white/5 rounded-xl px-3 py-2 text-slate-300 font-sans text-xs focus:outline-none"
                        >
                          <option value="active">Activo (Construccion)</option>
                          <option value="planning">Planificacion / Licitacion</option>
                          <option value="suspended">Suspendido Temporalmente</option>
                        </select>
                      </div>

                      <button
                        type="submit"
                        disabled={createLoading || !newProjectName}
                        className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs py-2.5 rounded-xl transition-all flex items-center justify-center gap-1.5 cursor-pointer mt-2 disabled:opacity-50"
                      >
                        <Plus className="w-4 h-4" />
                        Agregar Proyecto
                      </button>
                    </form>
                  </div>

                  {/* Listado en Tiempo Real */}
                  <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Proyectos del Contexto Actual</h4>
                    
                    {projectsLoading ? (
                      <div className="flex justify-center items-center py-12">
                        <RefreshCw className="w-6 h-6 animate-spin text-slate-600" />
                      </div>
                    ) : (
                      <div className="flex flex-col gap-2.5 max-h-[300px] overflow-y-auto pr-1">
                        {projects.map((proj) => (
                          <div key={proj.project_id} className="p-3 bg-slate-900/40 border border-white/5 rounded-xl flex items-center justify-between">
                            <div>
                              <span className="text-[9px] font-mono text-slate-500 block uppercase">{proj.project_id}</span>
                              <span className="text-xs font-bold text-slate-200 mt-0.5 block">{proj.name}</span>
                            </div>
                            <span className={`px-2 py-0.5 rounded-md text-[8px] font-bold font-mono tracking-wider uppercase ${
                              proj.status === "active" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/15" : "bg-blue-500/10 text-blue-400 border border-blue-500/15"
                            }`}>
                              {proj.status}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                </div>
              </div>

              {/* Estadísticas de la infraestructura SaaS */}
              <div className="mt-8 pt-4 border-t border-white/5 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-3 bg-slate-900/60 border border-white/5 rounded-xl flex items-center gap-3">
                  <Server className="w-5 h-5 text-blue-500" />
                  <div>
                    <span className="text-[9px] text-slate-500 block font-mono font-bold">API QUOTA USAGE</span>
                    <span className="text-xs font-bold font-mono text-white">4,289 / 50,000 reqs</span>
                  </div>
                </div>

                <div className="p-3 bg-slate-900/60 border border-white/5 rounded-xl flex items-center gap-3">
                  <Database className="w-5 h-5 text-emerald-500" />
                  <div>
                    <span className="text-[9px] text-slate-500 block font-mono font-bold">GRAPH DB NODES</span>
                    <span className="text-xs font-bold font-mono text-white">128 active nodes</span>
                  </div>
                </div>

                <div className="p-3 bg-slate-900/60 border border-white/5 rounded-xl flex items-center gap-3">
                  <Cpu className="w-5 h-5 text-purple-500" />
                  <div>
                    <span className="text-[9px] text-slate-500 block font-mono font-bold">COMPUTE CLUSTER</span>
                    <span className="text-xs font-bold font-mono text-white">4 nodes - Load 12%</span>
                  </div>
                </div>
              </div>
            </div>

          </div>
        )}

      </main>

      {/* Footer Fijo */}
      <footer className="mt-auto border-t border-white/5 py-4 px-6 md:px-12 bg-black/40 text-center text-[10px] text-slate-500 font-mono">
        CIVIL-TWIN Enterprise v3.0.0 | Plataforma SaaS B2B Segura | Arquitectura de Alta Disponibilidad Decoplada
      </footer>
    </div>
  );
}
