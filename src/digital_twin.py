import pandas as pd

class DigitalTwinEngine:
    """Motor del Gemelo Digital y control de costes mediante Earned Value Management (EVM) Granular"""
    def __init__(self, budget=0.0, total_days=0):
        self.budget = budget
        self.total_days = total_days

    def calculate_evm_granular(self, day: int, tasks_df: pd.DataFrame):
        """
        Calcula las métricas EVM iterando por cada unidad de obra (WBS).
        tasks_df debe contener 'Start_Day', 'Duration', 'Cost', 'Actual_Progress', 'Actual_Cost'.
        """
        pv_total = 0.0
        ev_total = 0.0
        ac_total = 0.0
        budget_total = 0.0

        if tasks_df.empty:
            return self._build_metrics_dict(day, pv_total, ev_total, ac_total, budget_total)

        for _, row in tasks_df.iterrows():
            start = row.get("Start_Day", 1)
            duration = row.get("Duration", 1)
            cost = row.get("Cost", 0.0)
            actual_progress = row.get("Actual_Progress", 0.0)
            actual_cost = row.get("Actual_Cost", 0.0)
            
            end = start + duration - 1
            budget_total += cost
            
            # Planned Value for this task
            task_pv = 0.0
            if day > end:
                task_pv = cost
            elif day >= start:
                task_pv = ((day - start + 1) / duration) * cost
                
            pv_total += task_pv
            
            # Earned Value for this task (fisico % * presu_tarea)
            ev_total += (actual_progress * cost)
            
            # Actual Cost for this task
            ac_total += actual_cost

        return self._build_metrics_dict(day, pv_total, ev_total, ac_total, budget_total)

    def _build_metrics_dict(self, day, pv, ev, ac, budget):
        cv = ev - ac
        sv = ev - pv
        cpi = ev / ac if ac > 0 else 1.0
        spi = ev / pv if pv > 0 else 1.0
        eac = budget / cpi if cpi > 0 else budget
        vac = budget - eac

        return {
            "Day": day,
            "PV": pv,
            "EV": ev,
            "AC": ac,
            "CV": cv,
            "SV": sv,
            "CPI": cpi,
            "SPI": spi,
            "EAC": eac,
            "VAC": vac,
            "Budget": budget
        }

    def get_alerts(self, metrics):
        alerts = []
        cpi = metrics.get("CPI", 1.0)
        spi = metrics.get("SPI", 1.0)
        vac = metrics.get("VAC", 0.0)

        if cpi < 0.85:
            alerts.append({"type": "CRITICAL", "message": f"Sobrecoste Crítico (CPI = {cpi:.2f}). Pérdida estimada: €{abs(vac):,.0f}"})
        elif cpi < 0.95:
            alerts.append({"type": "WARNING", "message": f"Advertencia Coste: Tendencia a desvío (CPI = {cpi:.2f})."})

        if spi < 0.85:
            alerts.append({"type": "CRITICAL", "message": f"Retraso Crítico en Plazos (SPI = {spi:.2f})."})
        elif spi < 0.95:
            alerts.append({"type": "WARNING", "message": f"Advertencia Plazo: Retraso acumulado (SPI = {spi:.2f})."})

        if not alerts:
            alerts.append({"type": "SUCCESS", "message": "EVM en parámetros estables (CPI y SPI > 0.95)."})

        return alerts
