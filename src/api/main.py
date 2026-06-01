from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd

from src.core.engine import MonteCarloSimulator, KnowledgeGraphEngine, BayesianRiskEngine

app = FastAPI(
    title="CIVIL-TWIN Enterprise API",
    description="SaaS B2B Backend de grado empresarial para simulaciones tecnicas y analisis de riesgos de obra civil",
    version="3.0.0"
)

# Configuracion de CORS para permitir la comunicacion con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Base de datos en memoria simulada para Tenants y Proyectos B2B
VALID_TENANTS = {
    "token_fuerteventura_enterprise": {
        "tenant_id": "tenant_fuerteventura_civil",
        "name": "Fuerteventura Civil S.A.",
        "tier": "Enterprise"
    },
    "token_agaete_consorcio": {
        "tenant_id": "tenant_agaete_consorcio",
        "name": "Consorcio Vial Agaete",
        "tier": "Premium"
    }
}

TENANT_PROJECTS = {
    "tenant_fuerteventura_civil": [
        {"project_id": "proj_fv_001", "name": "Autovia Puerto del Rosario - Caldereta", "status": "active"},
        {"project_id": "proj_fv_002", "name": "Duplicacion de Calzada Aeropuerto", "status": "planning"}
    ],
    "tenant_agaete_consorcio": [
        {"project_id": "proj_ag_101", "name": "Tramo Carretera El Risco - Agaete", "status": "active"}
    ]
}

# Modelos de peticion y respuesta Pydantic
class TaskItem(BaseModel):
    Task_ID: int
    Task: str
    Duration: float
    Cost: float
    Start_Day: int
    Predecessors: Optional[str] = ""

class MonteCarloRequest(BaseModel):
    tasks: List[TaskItem]
    rmr: float = 60.0
    water_influx: float = 15.0
    depth: float = 80.0
    iterations: int = 2000

class RAGIngestRequest(BaseModel):
    document_name: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ProjectCreateRequest(BaseModel):
    project_id: str
    name: str
    status: str

# Dependencia para verificar tenant multi-tenant basico
def get_current_tenant(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    token = credentials.credentials
    if token not in VALID_TENANTS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de tenant invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return VALID_TENANTS[token]

# Instanciacion de motores Core
montecarlo_simulator = MonteCarloSimulator()
graph_engine = KnowledgeGraphEngine()
bayesian_engine = BayesianRiskEngine()

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "CIVIL-TWIN Backend",
        "architecture": "SaaS B2B Decoupled"
    }

@app.post("/simulate/montecarlo")
async def simulate_montecarlo(request: MonteCarloRequest):
    """
    Endpoint para realizar simulaciones vectorizadas de Monte Carlo.
    Recibe la WBS (lista de tareas) y los parametros del frente de excavacion.
    """
    try:
        # Transformar lista de tareas en DataFrame
        tasks_data = [task.model_dump() for task in request.tasks]
        tasks_df = pd.DataFrame(tasks_data)
        
        # Ejecutar simulacion
        results = montecarlo_simulator.run_simulation(
            tasks_df=tasks_df,
            rmr=request.rmr,
            water_influx=request.water_influx,
            depth=request.depth,
            iterations=request.iterations
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante la simulacion: {str(e)}"
        )

@app.get("/tenant/projects", response_model=List[Dict[str, Any]])
async def get_tenant_projects(tenant: Dict[str, Any] = Depends(get_current_tenant)):
    """
    Endpoint protegido B2B Multi-Tenant.
    Retorna los proyectos autorizados correspondientes al Tenant del Token.
    """
    tenant_id = tenant["tenant_id"]
    projects = TENANT_PROJECTS.get(tenant_id, [])
    return projects

@app.post("/tenant/projects", status_code=status.HTTP_201_CREATED)
async def create_tenant_project(project: ProjectCreateRequest, tenant: Dict[str, Any] = Depends(get_current_tenant)):
    """
    Crea un nuevo proyecto bajo el contexto del Tenant actual.
    """
    tenant_id = tenant["tenant_id"]
    if tenant_id not in TENANT_PROJECTS:
        TENANT_PROJECTS[tenant_id] = []
    
    new_project = project.model_dump()
    TENANT_PROJECTS[tenant_id].append(new_project)
    return {
        "message": "Proyecto creado exitosamente",
        "project": new_project,
        "tenant_owner": tenant["name"]
    }

@app.post("/rag/ingest")
async def ingest_document_rag(request: RAGIngestRequest):
    """
    Endpoint preparado para la ingestion de documentos tecnicos de ingenieria civil.
    Construye las relaciones semanticas dentro del motor de Grafo de Conocimiento (KnowledgeGraphEngine).
    """
    try:
        # Analizar semanticamente el documento para extraer entidades y relaciones
        # Simula integracion basica mapeando el documento
        doc_id = request.document_name.replace(" ", "_").upper()
        graph_engine.add_entity(doc_id, {
            "tipo": "Especificacion_Tecnica",
            "nombre": request.document_name,
            "tamano_caracteres": len(request.content)
        })
        
        # Enlazar con el proyecto si se incluye en metadata
        project_link = request.metadata.get("project_id") if request.metadata else None
        if project_link:
            graph_engine.add_entity(project_link, {"tipo": "Proyecto_Obra"})
            graph_engine.add_relation(project_link, doc_id, "regulada_por")
            
        subgraph = graph_engine.query_subgraph(doc_id)
        
        return {
            "status": "success",
            "message": f"Documento {request.document_name} indexado y mapeado en Knowledge Graph",
            "extracted_subgraph": subgraph
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante la ingesta documental en el Knowledge Graph: {str(e)}"
        )

@app.get("/rag/graph/{entity_id}")
async def query_knowledge_graph(entity_id: str):
    """
    Consulta el estado actual de relaciones de una entidad en el Grafo de Conocimiento.
    """
    subgraph = graph_engine.query_subgraph(entity_id)
    return subgraph
