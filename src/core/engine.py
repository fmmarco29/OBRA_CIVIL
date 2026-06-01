import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import networkx as nx
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from typing import List, Dict, Any, Union

class GeotechnicalRiskModel:
    """Clase para clasificar riesgos geotécnicos usando machine learning local con datos pre-entrenados"""
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False

    def generate_synthetic_data(self, size=2000):
        """
        Genera un dataset sintético con correlación geológica real para entrenamiento.
        Factores de entrada:
        - RMR (Rock Mass Rating): 0 a 100
        - Profundidad (m): 10 a 500
        - Flujo de agua freática (L/min): 0 a 120
        """
        np.random.seed(42)
        rmr = np.random.uniform(15, 85, size)
        depth = np.random.uniform(20, 450, size)
        water_influx = np.random.uniform(0, 100, size)
        
        # Logica heuristica para determinar etiquetas de riesgo (0: Bajo, 1: Medio, 2: Alto)
        labels = []
        for r, d, w in zip(rmr, depth, water_influx):
            score = 0.0
            
            # Impacto del RMR (roca mala aumenta el riesgo notablemente)
            if r < 35:
                score += 4.5
            elif r < 55:
                score += 2.5
            else:
                score += 0.5
                
            # Impacto de la profundidad (mayor profundidad aumenta la presion de la roca)
            if d > 250:
                score += 2.5
            elif d > 120:
                score += 1.2
            else:
                score += 0.2
                
            # Impacto del flujo de agua freatica (filtraciones)
            if w > 50:
                score += 3.5
            elif w > 15:
                score += 1.5
            else:
                score += 0.1
                
            # Umbrales
            if score < 2.5:
                labels.append(0)  # Bajo
            elif score < 5.5:
                labels.append(1)  # Medio
            else:
                labels.append(2)  # Alto
                
        X = np.column_stack((rmr, depth, water_influx))
        y = np.array(labels)
        return X, y

    def train(self):
        """Entrena el modelo en local con el dataset sintetico representativo de ingenieria de tuneles"""
        X, y = self.generate_synthetic_data()
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, features):
        """
        Predice el nivel de riesgo para una o varias muestras.
        Argumentos:
        - features: list de listas o array de forma (n_muestras, 3) con formato [[RMR, Depth, Water_Influx]]
        Retorna:
        - array con etiquetas de riesgo (0, 1, 2)
        """
        if not self.is_trained:
            self.train()
        return self.model.predict(features)

    def predict_proba(self, features):
        """Retorna las probabilidades para cada clase de riesgo"""
        if not self.is_trained:
            self.train()
        return self.model.predict_proba(features)


class MonteCarloSimulator:
    """Clase para la simulacion probabilistica de costes y plazos de la obra de la carretera con tunel de 200ME"""
    def __init__(self):
        pass

    def run_simulation(self, tasks_df: pd.DataFrame, rmr: float = 60, water_influx: float = 15, depth: float = 80, iterations: int = 2000) -> Dict[str, Any]:
        """
        Ejecuta una simulacion de Monte Carlo vectorizada en base a la WBS cargada y parametros de riesgo geotecnico.
        Modifica la variabilidad de las tareas basandose en el riesgo geotecnico del tunel.
        Altamente optimizada utilizando operaciones vectoriales de NumPy.
        """
        np.random.seed(42)
        
        # Calcular el riesgo geotecnico del tunel
        risk_model = GeotechnicalRiskModel()
        risk_class = int(risk_model.predict([[rmr, depth, water_influx]])[0])
        
        # Multiplicadores de riesgo en base a la severidad geotecnica (tunel)
        risk_factor_cost = 1.0
        risk_factor_time = 1.0
        if risk_class == 1:    # Medio
            risk_factor_cost = 1.15
            risk_factor_time = 1.20
        elif risk_class == 2:  # Alto
            risk_factor_cost = 1.40
            risk_factor_time = 1.55

        # Diccionarios para almacenar las muestras aleatorias de duraciones y costes por Task_ID
        sim_durations = {}
        sim_costs = {}
        task_end_days = {} # Almacena array de duraciones acumuladas por Task_ID para todas las iteraciones

        # Convertir a lista de registros para evitar el coste de iterrows de pandas en el bucle principal
        tasks = tasks_df.to_dict('records')

        # 1. Generacion vectorizada de muestras aleatorias triangulares (PERT)
        for row in tasks:
            tid = int(row["Task_ID"])
            duration_base = float(row["Duration"])
            cost_base = float(row["Cost"])

            # Determinar multiplicadores individuales segun el tipo de tarea (Tunel sensible a riesgos)
            if tid in [4, 5]:
                task_time_mult = risk_factor_time
                task_cost_mult = risk_factor_cost
            else:
                task_time_mult = 1.05
                task_cost_mult = 1.05

            # Limites PERT
            t_opt = duration_base * 0.90
            t_prob = duration_base
            t_pes = duration_base * (1.10 + (task_time_mult - 1.0) * 1.5)
            
            c_opt = cost_base * 0.95
            c_prob = cost_base
            c_pes = cost_base * (1.05 + (task_cost_mult - 1.0) * 1.4)

            # Muestreo vectorizado de NumPy (N muestras en una sola llamada de C nativo)
            sim_durations[tid] = np.random.triangular(t_opt, t_prob, t_pes, size=iterations)
            sim_costs[tid] = np.random.triangular(c_opt, c_prob, c_pes, size=iterations)

        # 2. Resolucion de la ruta critica y fechas de finalizacion de forma vectorizada
        for row in tasks:
            tid = int(row["Task_ID"])
            predecessors_str = str(row["Predecessors"]).strip()

            # Calcular el dia de inicio para las 'iterations' iteraciones de forma vectorizada
            start_days = np.ones(iterations)
            
            if predecessors_str and predecessors_str != "nan" and predecessors_str != "":
                pred_list = [int(x.strip()) for x in predecessors_str.split(",") if x.strip().isdigit()]
                if pred_list:
                    # Array elemental de NumPy conteniendo el maximo dia final de predecesores iteracion a iteracion
                    pred_ends = [task_end_days[p] for p in pred_list if p in task_end_days]
                    if pred_ends:
                        start_days = np.maximum.reduce(pred_ends) + 1

            # Calcular fin de la tarea vectorizado
            task_end_days[tid] = start_days + sim_durations[tid]

        # La duracion del proyecto para cada iteracion es el maximo de finalizacion de todas las tareas
        simulated_durations = np.maximum.reduce(list(task_end_days.values()))
        # El coste total para cada iteracion es la suma de los costes simulados de todas las tareas
        simulated_costs = np.sum(list(sim_costs.values()), axis=0)

        # Estadisticas y cuantiles en base a los resultados simulados
        results = {
            "durations": simulated_durations.tolist(),
            "costs": simulated_costs.tolist(),
            "p10_duration": int(np.percentile(simulated_durations, 10)),
            "p50_duration": int(np.percentile(simulated_durations, 50)),
            "p90_duration": int(np.percentile(simulated_durations, 90)),
            "p10_cost": float(np.percentile(simulated_costs, 10)),
            "p50_cost": float(np.percentile(simulated_costs, 50)),
            "p90_cost": float(np.percentile(simulated_costs, 90)),
            "geotechnical_risk_level": risk_class
        }

        return results


class KnowledgeGraphEngine:
    """Clase base para el sistema de Grafo de Conocimiento y Graph RAG (Preparado para PDFs de ingenieria civil)"""
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_entity(self, entity_id: str, properties: Dict[str, Any]) -> None:
        """Agrega una entidad al grafo de conocimiento"""
        self.graph.add_node(entity_id, **properties)

    def add_relation(self, source_id: str, target_id: str, relation_type: str, properties: Dict[str, Any] = None) -> None:
        """Agrega una relacion dirigida entre entidades"""
        if properties is None:
            properties = {}
        self.graph.add_edge(source_id, target_id, relation_type=relation_type, **properties)

    def query_subgraph(self, root_entity: str, max_depth: int = 2) -> Dict[str, Any]:
        """Extrae un subgrafo local centrado en una entidad para alimentar el contexto del RAG"""
        if root_entity not in self.graph:
            return {"nodes": [], "edges": []}
        
        subgraph = nx.ego_graph(self.graph, root_entity, radius=max_depth)
        nodes = [{"id": node, "properties": subgraph.nodes[node]} for node in subgraph.nodes]
        edges = [{"source": u, "target": v, "type": data.get("relation_type", "related")} 
                 for u, v, data in subgraph.edges(data=True)]
        
        return {"nodes": nodes, "edges": edges}

    def process_civil_pdf_structure(self, pdf_path: str) -> None:
        """Metodo de interfaz para procesar e integrar pliegos tecnicos de ingenieria en el grafo de conocimiento"""
        # Placeholder estructurado para la futura implementacion del extractor RAG (ej. Carretera El Risco-Agaete)
        self.add_entity("PROYECTO_EL_RISCO_AGAETE", {
            "tipo": "Proyecto_Carretera", 
            "tramo": "El Risco - Agaete", 
            "longitud_total_km": 7.8
        })
        self.add_entity("TUNEL_FANIEGUE", {
            "tipo": "Tunel", 
            "longitud_m": 2100, 
            "geologia_principal": "Basaltos"
        })
        self.add_relation("PROYECTO_EL_RISCO_AGAETE", "TUNEL_FANIEGUE", "contiene_elemento")


class BayesianRiskEngine:
    """Clase base para el motor de riesgos probabilisticos mediante Redes Bayesianas"""
    def __init__(self):
        self.model = None
        self.inference = None

    def setup_default_network(self) -> None:
        """Configura una red bayesiana de ejemplo para riesgos de excavacion y estabilidad"""
        # Estructura: Geologia -> Estabilidad del Frente; Filtraciones -> Estabilidad del Frente; Estabilidad del Frente -> Retraso
        self.model = BayesianNetwork([
            ('Geologia', 'Estabilidad'),
            ('Filtraciones', 'Estabilidad'),
            ('Estabilidad', 'Retraso')
        ])

        # Definicion de Tablas de Probabilidad Condicional (CPDs)
        cpd_geologia = TabularCPD(variable='Geologia', variable_card=2, values=[[0.7], [0.3]], state_names={'Geologia': ['Buena', 'Mala']})
        cpd_filtraciones = TabularCPD(variable='Filtraciones', variable_card=2, values=[[0.8], [0.2]], state_names={'Filtraciones': ['Bajas', 'Altas']})
        
        cpd_estabilidad = TabularCPD(
            variable='Estabilidad', 
            variable_card=2, 
            values=[
                [0.95, 0.60, 0.70, 0.10], # Probabilidad de Estabilidad Estable
                [0.05, 0.40, 0.30, 0.90]  # Probabilidad de Inestabilidad
            ],
            evidence=['Geologia', 'Filtraciones'],
            evidence_card=[2, 2],
            state_names={
                'Estabilidad': ['Estable', 'Inestable'],
                'Geologia': ['Buena', 'Mala'],
                'Filtraciones': ['Bajas', 'Altas']
            }
        )
        
        cpd_retraso = TabularCPD(
            variable='Retraso', 
            variable_card=2, 
            values=[
                [0.90, 0.20], # Probabilidad de No Retraso
                [0.10, 0.80]  # Probabilidad de Retraso
            ],
            evidence=['Estabilidad'],
            evidence_card=[2],
            state_names={'Retraso': ['No', 'Si'], 'Estabilidad': ['Estable', 'Inestable']}
        )

        self.model.add_cpds(cpd_geologia, cpd_filtraciones, cpd_estabilidad, cpd_retraso)
        self.model.check_model()
        self.inference = VariableElimination(self.model)

    def calculate_risk_probability(self, evidence: Dict[str, Any]) -> Dict[str, float]:
        """Calcula la probabilidad posterior dado un conjunto de evidencias"""
        if self.model is None or self.inference is None:
            self.setup_default_network()
        
        result = self.inference.query(variables=['Retraso'], evidence=evidence)
        state_names = result.state_names['Retraso']
        probabilities = result.values
        
        return {state_names[i]: float(probabilities[i]) for i in range(len(state_names))}
