import pandas as pd
import numpy as np

class DigitalTwinEngine:
    """Clase para el Gemelo Digital y control de costes mediante Earned Value Management (EVM)"""
    def __init__(self, budget=200000000.0, total_days=730):
        self.budget = budget
        self.total_days = total_days

    def calculate_evm(self, day, actual_cost, actual_progress, tasks_df):
        """
        Calcula las métricas de Gestión del Valor Ganado (EVM) comparando la línea base planificada
        con el progreso y coste reales del proyecto en un día específico.
        """
        # 1. Planned Value (PV)
        # Calculamos cuánto presupuesto deberíamos haber gastado planificadamente hasta el 'day' actual
        pv = 0.0
        for _, row in tasks_df.iterrows():
            start = row["Start_Day"]
            duration = row["Duration"]
            cost = row["Cost"]
            end = start + duration - 1
            
            if day > end:
                # La actividad ya debería haber terminado
                pv += cost
            elif day < start:
                # La actividad aún no debería haber comenzado
                pv += 0.0
            else:
                # La actividad debería estar en curso (proporción lineal planificada)
                fraction = (day - start + 1) / duration
                pv += fraction * cost

        # 2. Earned Value (EV)
        # Es la representación en dinero del avance real del proyecto
        ev = actual_progress * self.budget

        # 3. Actual Cost (AC)
        # Dinero realmente gastado reportado
        ac = actual_cost

        # 4. Varianzas
        cv = ev - ac  # Cost Variance (positivo = ahorro, negativo = sobrecoste)
        sv = ev - pv  # Schedule Variance (positivo = adelanto, negativo = retraso)

        # 5. Índices de Rendimiento
        cpi = ev / ac if ac > 0 else 1.0
        spi = ev / pv if pv > 0 else 1.0

        # 6. Estimaciones finales
        eac = self.budget / cpi if cpi > 0 else self.budget
        etc = eac - ac
        vac = self.budget - eac  # Variance at Completion (positivo = ahorro al final, negativo = pérdida)

        metrics = {
            "Day": day,
            "PV": pv,
            "EV": ev,
            "AC": ac,
            "CV": cv,
            "SV": sv,
            "CPI": cpi,
            "SPI": spi,
            "EAC": eac,
            "ETC": etc,
            "VAC": vac,
            "Budget": self.budget,
            "Total_Days": self.total_days
        }

        return metrics

    def get_alerts(self, metrics):
        """
        Analiza las desviaciones del Gemelo Digital y emite alertas de tipo advertencia o crítico.
        """
        alerts = []
        cpi = metrics["CPI"]
        spi = metrics["SPI"]
        cv = metrics["CV"]
        sv = metrics["SV"]

        # Alertas de sobrecoste (CPI)
        if cpi < 0.85:
            alerts.append({
                "type": "CRITICAL",
                "component": "COSTS",
                "message": f"Desviación Crítica en Costes: El CPI es {cpi:.2f} (límite < 0.85). Pérdida estimada al finalizar (VAC) de €{abs(metrics['VAC']):,.2f}."
            })
        elif cpi < 0.92:
            alerts.append({
                "type": "WARNING",
                "component": "COSTS",
                "message": f"Advertencia de Costes: Tendencia al sobrecoste. El rendimiento es de CPI = {cpi:.2f}. Se está gastando más de lo planificado por unidad de avance."
            })

        # Alertas de plazo (SPI)
        if spi < 0.85:
            alerts.append({
                "type": "CRITICAL",
                "component": "SCHEDULE",
                "message": f"Retraso Crítico en Plazos: El SPI es {spi:.2f} (límite < 0.85). La obra acumula una desviación temporal acumulada de €{abs(sv):,.2f} en valor de avance."
            })
        elif spi < 0.92:
            alerts.append({
                "type": "WARNING",
                "component": "SCHEDULE",
                "message": f"Advertencia de Plazos: Retraso acumulado moderado (SPI = {spi:.2f}). Se requiere revisar la ruta crítica y optimizar rendimientos en la excavación."
            })

        # Si todo va bien
        if not alerts:
            alerts.append({
                "type": "SUCCESS",
                "component": "GENERAL",
                "message": "Operaciones dentro del margen de tolerancia. Rendimiento del proyecto óptimo y estable."
            })

        return alerts
