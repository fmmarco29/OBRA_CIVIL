import datetime

class LaTeXReportGenerator:
    """Clase para la generación automática de informes técnicos ejecutivos en LaTeX para la dirección de obra"""
    def __init__(self):
        pass

    def generate_report(self, metadata, evm_metrics, risk_results):
        """
        Genera el código LaTeX del informe ejecutivo basado en el estado diario del Gemelo Digital
        y las predicciones del motor de riesgos.
        """
        # Formatear valores numéricos para visualización legible
        budget = metadata.get("budget", 200000000.0)
        tunnel_len = metadata.get("tunnel_length", 1450.0)
        duration_days = metadata.get("duration_days", 730)
        geology = metadata.get("geology", "N/A")
        water = metadata.get("water_table", "N/A")

        day = evm_metrics.get("Day", 0)
        pv = evm_metrics.get("PV", 0.0)
        ev = evm_metrics.get("EV", 0.0)
        ac = evm_metrics.get("AC", 0.0)
        cv = evm_metrics.get("CV", 0.0)
        sv = evm_metrics.get("SV", 0.0)
        cpi = evm_metrics.get("CPI", 1.0)
        spi = evm_metrics.get("SPI", 1.0)
        eac = evm_metrics.get("EAC", budget)
        vac = evm_metrics.get("VAC", 0.0)

        p50_t = risk_results.get("p50_duration", duration_days)
        p90_t = risk_results.get("p90_duration", duration_days)
        p50_c = risk_results.get("p50_cost", budget)
        p90_c = risk_results.get("p90_cost", budget)
        risk_class = risk_results.get("geotechnical_risk_level", 0)

        risk_str = ["BAJO", "MEDIO", "ALTO"][risk_class]
        risk_color = ["greenalert", "orangealert", "redalert"][risk_class]

        date_str = datetime.date.today().strftime("%d/%m/%Y")

        # Plantilla LaTeX elegante y profesional
        latex_template = f"""\\documentclass[11pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[spanish]{{babel}}
\\usepackage{{geometry}}
\\geometry{{left=2.5cm,right=2.5cm,top=3cm,bottom=3cm}}
\\usepackage{{booktabs}}
\\usepackage{{xcolor}}
\\usepackage{{titlesec}}
\\usepackage{{fancyhdr}}
\\usepackage{{hyperref}}

% Colores corporativos de ingeniería
\\definecolor{{brandblue}}{{HTML}}{{1A365D}}
\\definecolor{{brandgray}}{{HTML}}{{4A5568}}
\\definecolor{{redalert}}{{HTML}}{{E53E3E}}
\\definecolor{{orangealert}}{{HTML}}{{DD6B20}}
\\definecolor{{greenalert}}{{HTML}}{{38A169}}

\\hypersetup{{
    colorlinks=true,
    linkcolor=brandblue,
    urlcolor=brandblue
}}

\\titleformat{{\\section}}
  {{\\normalfont\\Large\\bfseries\\color{{brandblue}}}}{{\\thesection}}{{1em}}{{}}[\\titlerule]
\\titleformat{{\\subsection}}
  {{\\normalfont\\large\\bfseries\\color{{brandgray}}}}{{\\thesubsection}}{{1em}}{{}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\lhead{{\\color{{brandgray}}CIVIL-TWIN: Gemelo Digital de Carretera con Túnel (Fuerteventura)}}
\\rhead{{\\color{{brandgray}}Informe de Obra - {date_str}}}
\\cfoot{{\\thepage}}

\\begin{{document}}

\\begin{{center}}
    {{\\Huge \\bfseries \\color{{brandblue}} INFORME EJECUTIVO DE CONTROL DE OBRA}} \\\\[0.4cm]
    {{\\large \\bfseries \\color{{brandgray}} Carretera Puerto del Rosario - Caldereta (Túnel Singulado) }} \\\\[0.2cm]
    {{\\large \\bfseries Presupuesto: €{budget:,.2f} | Plazo Base: {duration_days} días}} \\\\[0.8cm]
\\end{{center}}

\\section{{Resumen del Proyecto e Ingestión Documental}}
Este informe técnico ha sido generado automáticamente por el Gemelo Digital \\textbf{{CIVIL-TWIN}} en base a los datos extraídos de los pliegos técnicos y el diario de obra procesados localmente mediante técnicas de Procesamiento de Lenguaje Natural (NLP).

\\subsection{{Metadatos del Proyecto Extraídos Localmente}}
\\begin{{itemize}}
    \\item \\textbf{{Presupuesto Base de Licitación (BAC):}} €{budget:,.2f}
    \\item \\textbf{{Longitud de Excavación del Túnel:}} {tunnel_len:,.2f} metros.
    \\item \\textbf{{Plazo Total Planificado:}} {duration_days} días naturales.
    \\item \\textbf{{Geología Dominante del Frente:}} {geology}
    \\item \\textbf{{Condiciones Hidrogeológicas / Nivel Freático:}} {water}
\\end{{itemize}}

\\section{{Análisis del Valor Ganado (EVM) - Día {day}}}
El estado actual de la obra en el \\textbf{{Día {day}}} ha sido comparado detalladamente con la línea de base del cronograma (Gantt) y los costes acumulados reportados en la obra.

\\begin{{table}}[h!]
\\centering
\\caption{{Indicadores Clave de Rendimiento Financiero y Plazo (EVM)}}
\\vspace{{0.2cm}}
\\begin{{tabular}}{{lc}}
\\toprule
\\textbf{{Métrica de Control}} & \\textbf{{Valor (€ / Ratio)}} \\\\
\\midrule
Presupuesto Total del Proyecto (BAC) & €{budget:,.2f} \\\\
Valor Planificado (PV) & €{pv:,.2f} \\\\
Valor Ganado (EV) & €{ev:,.2f} \\\\
Coste Real Incurrido (AC) & €{ac:,.2f} \\\\
\\midrule
Varianza de Coste (CV) & €{cv:,.2f} \\\\
Varianza de Plazo (SV) & €{sv:,.2f} \\\\
\\midrule
\\textbf{{Índice de Rendimiento de Costes (CPI)}} & \\textbf{{{cpi:.3f}}} \\\\
\\textbf{{Índice de Rendimiento de Plazo (SPI)}} & \\textbf{{{spi:.3f}}} \\\\
\\midrule
Estimado al Finalizar (EAC) & €{eac:,.2f} \\\\
Desviación Estimada al Finalizar (VAC) & €{vac:,.2f} \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}

\\subsection{{Diagnóstico del Gemelo Digital}}
{f"El proyecto presenta un \\textbf{{sobrecoste acumulado}} de €{abs(cv):,.2f} respecto al avance real logrado." if cv < 0 else "El proyecto se encuentra en una situación de \\textbf{{ahorro en costes}} respecto al avance logrado."}
{f"Asimismo, se registra un \\textbf{{retraso temporal}} equivalente a €{abs(sv):,.2f} en valor de obra no ejecutada." if sv < 0 else "De igual modo, el avance temporal está \\textbf{{adelantado}} respecto al cronograma de referencia."}

\\section{{Simulación de Monte Carlo y Predicción de Riesgos Geotécnicos}}
Mediante modelos de Machine Learning (Random Forest) entrenados con bases de datos públicas de seguridad e infraestructuras, se clasifica el nivel de riesgo geotécnico en el frente de excavación del túnel. Adicionalmente, se ejecuta una simulación de Monte Carlo con 5.000 iteraciones para prever los escenarios de costes y plazos finales bajo incertidumbre.

\\subsection{{Clasificación de Riesgo Geotécnico (Frente de Túnel)}}
\\begin{{itemize}}
    \\item \\textbf{{Nivel de Riesgo Predictivo del Frente:}} \\textbf{{\\color{{{risk_color}}} {risk_str}}}
    \\item \\textbf{{Variables del Frente de Excavación:}} Basado en un RMR de la roca, profundidad del túnel y posible flujo de filtración de agua freática en la zona activa.
\\end{{itemize}}

\\subsection{{Resultados Probabilísticos de la Simulación de Plazos y Costes}}
La simulación probabilística estima los siguientes percentiles para la finalización del proyecto de la carretera con túnel de €200M:
\\begin{{itemize}}
    \\item \\textbf{{Duración P50 (Escenario Más Probable):}} \\textbf{{{p50_t}}} días (Desviación respecto a la base: {p50_t - duration_days} días).
    \\item \\textbf{{Duración P90 (Escenario Pesimista / Riesgo Alto):}} \\textbf{{{p90_t}}} días (Desviación respecto a la base: {p90_t - duration_days} días).
    \\item \\textbf{{Coste P50 (Costo Final Probable):}} €{p50_c:,.2f}
    \\item \\textbf{{Coste P90 (Costo Final en Peor Escenario):}} €{p90_c:,.2f} (Incremento del {((p90_c - budget) / budget) * 100:.1f}\\% sobre el presupuesto base).
\\end{{itemize}}

\\section{{Recomendaciones para la Dirección de Obra}}
Basándose en el estado diario del Gemelo Digital y las predicciones probabilísticas, se aconsejan las siguientes medidas correctoras inmediatas:
\\begin{{enumerate}}
    \\item \\textbf{{Si el Riesgo Geotécnico es ALTO:}} Reforzar la colocación de cerchas metálicas y bulones de anclaje de manera inmediata en la zona de excavación activa. Implementar paraguas de micropilotes en caso de empeoramiento del RMR.
    \\item \\textbf{{Si el CPI < 0.90:}} Iniciar auditoría de costes de subcontratación de maquinaria pesada de excavación y revisar rendimientos del ciclo de carga y transporte.
    \\item \\textbf{{Si el SPI < 0.90:}} Aumentar turnos de trabajo en el emboquille del túnel y reprogramar actividades no críticas de la carretera en paralelo para recuperar el retraso en la ruta crítica.
\\end{{enumerate}}

\\vspace{{1.5cm}}
\\begin{{center}}
    \\begin{{minipage}}{{0.4\\textwidth}}
        \\centering
        \\rule{{\\textwidth}}{{0.4pt}} \\\\[0.1cm]
        \\textbf{{Dirección de Obra}} \\\\
        Fuerteventura
    \\end{{minipage}}
    \\hfill
    \\begin{{minipage}}{{0.4\\textwidth}}
        \\centering
        \\rule{{\\textwidth}}{{0.4pt}} \\\\[0.1cm]
        \\textbf{{CIVIL-TWIN System}} \\\\
        Arquitectura IA Local
    \\end{{minipage}}
\\end{{center}}

\\end{{document}}
"""
        return latex_template
