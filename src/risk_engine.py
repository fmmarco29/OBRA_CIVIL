import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

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
        
        # Lógica heurística para determinar etiquetas de riesgo (0: Bajo, 1: Medio, 2: Alto)
        labels = []
        for r, d, w in zip(rmr, depth, water_influx):
            # Puntaje de riesgo (a mayor puntaje, mayor riesgo)
            score = 0.0
            
            # Impacto del RMR (roca mala aumenta el riesgo notablemente)
            if r < 35:
                score += 4.5
            elif r < 55:
                score += 2.5
            else:
                score += 0.5
                
            # Impacto de la profundidad (mayor profundidad aumenta la presión de la roca y de la tuneladora)
            if d > 250:
                score += 2.5
            elif d > 120:
                score += 1.2
            else:
                score += 0.2
                
            # Impacto del flujo de agua freática (filtraciones)
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
        """Entrena el modelo en local con el dataset sintético representativo de ingeniería de túneles"""
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
    """Clase para la simulación probabilística de costes y plazos de la obra de la carretera con túnel de 200M€"""
    def __init__(self):
        pass

    def run_simulation(self, tasks_df, rmr=60, water_influx=15, depth=80, iterations=2000):
        """
        Ejecuta una simulación de Monte Carlo en base a la WBS cargada y parámetros de riesgo geotécnico.
        Modifica la variabilidad de las tareas basándose en el riesgo geotécnico actual del túnel.
        """
        np.random.seed(42)
        
        # Calcular el riesgo geotécnico del túnel
        risk_model = GeotechnicalRiskModel()
        risk_class = risk_model.predict([[rmr, depth, water_influx]])[0]
        
        # Multiplicadores de riesgo en base a la severidad geotécnica
        # Afectan especialmente a la tarea del túnel (Task_ID 4, 5 y 6)
        risk_factor_cost = 1.0
        risk_factor_time = 1.0
        if risk_class == 1:    # Medio
            risk_factor_cost = 1.15
            risk_factor_time = 1.20
        elif risk_class == 2:  # Alto
            risk_factor_cost = 1.40
            risk_factor_time = 1.55

        simulated_durations = []
        simulated_costs = []

        for _ in range(iterations):
            total_duration = 0
            total_cost = 0.0
            task_end_days = {} # Guardar día de finalización simulado por Task_ID para modelar dependencias

            for _, row in tasks_df.iterrows():
                tid = row["Task_ID"]
                duration_base = row["Duration"]
                cost_base = row["Cost"]
                predecessors = str(row["Predecessors"]).strip()

                # Determinar multiplicadores individuales según el tipo de tarea
                # El túnel (Task_ID 4, 5) es muy sensible a riesgos geotécnicos
                if tid in [4, 5]:
                    task_time_mult = risk_factor_time
                    task_cost_mult = risk_factor_cost
                else:
                    task_time_mult = 1.05  # Menor influencia para carretera superficial
                    task_cost_mult = 1.05

                # Distribución triangular (PERT) para la tarea actual
                # Tiempo: Optimista (a), Probable (m), Pesimista (b)
                t_opt = duration_base * 0.90
                t_prob = duration_base
                t_pes = duration_base * (1.10 + (task_time_mult - 1.0) * 1.5)
                
                # Coste: Optimista (a), Probable (m), Pesimista (b)
                c_opt = cost_base * 0.95
                c_prob = cost_base
                c_pes = cost_base * (1.05 + (task_cost_mult - 1.0) * 1.4)

                sim_t = np.random.triangular(t_opt, t_prob, t_pes)
                sim_c = np.random.triangular(c_opt, c_prob, c_pes)

                # Calcular día de inicio simulado en base a predecesores
                start_day = 1
                if predecessors and predecessors != "nan" and predecessors != "":
                    pred_list = [int(x.strip()) for x in predecessors.split(",") if x.strip().isdigit()]
                    if pred_list:
                        # El inicio es el máximo final de sus predecesores
                        start_day = max(task_end_days.get(p, 1) for p in pred_list) + 1

                end_day = start_day + sim_t
                task_end_days[tid] = end_day
                
                total_cost += sim_c

            # La duración del proyecto es el día máximo de finalización de todas las tareas
            project_duration = max(task_end_days.values())
            simulated_durations.append(project_duration)
            simulated_costs.append(total_cost)

        simulated_durations = np.array(simulated_durations)
        simulated_costs = np.array(simulated_costs)

        # Estadísticas y cuantiles (P10, P50, P90)
        results = {
            "durations": simulated_durations,
            "costs": simulated_costs,
            "p10_duration": int(np.percentile(simulated_durations, 10)),
            "p50_duration": int(np.percentile(simulated_durations, 50)),
            "p90_duration": int(np.percentile(simulated_durations, 90)),
            "p10_cost": float(np.percentile(simulated_costs, 10)),
            "p50_cost": float(np.percentile(simulated_costs, 50)),
            "p90_cost": float(np.percentile(simulated_costs, 90)),
            "geotechnical_risk_level": risk_class  # 0: Bajo, 1: Medio, 2: Alto
        }

        return results
