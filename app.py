import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

from src.document_processor import DocumentProcessor
from src.risk_engine import GeotechnicalRiskModel, MonteCarloSimulator
from src.digital_twin import DigitalTwinEngine
from src.report_generator import LaTeXReportGenerator
from src.github_automation import GitHubAutomation

# Configuración de página con diseño responsive y moderno
st.set_page_config(
    page_title="CIVIL-TWIN | Fuerteventura Digital Twin",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilización premium con inyección de CSS estilo Glassmorphism y Dark Mode Tailored
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Fondo degradado y contenedor de la app */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(20, 24, 43, 1) 0%, rgba(8, 10, 15, 1) 100%);
        color: #E2E8F0;
    }
    
    /* Contenedor estilo Glassmorphism para KPI Cards */
    .kpi-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    .kpi-title {
        font-size: 0.85rem;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.2;
    }
    
    /* Alertas animadas premium */
    .alert-banner {
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
        border-left: 5px solid;
        animation: pulse 2s infinite alternate;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 10px rgba(255, 255, 255, 0.05); }
        100% { box-shadow: 0 0 20px rgba(255, 255, 255, 0.15); }
    }
    
    .alert-critical {
        background: rgba(239, 68, 68, 0.1);
        border-color: #EF4444;
        color: #FCA5A5;
    }
    
    .alert-warning {
        background: rgba(245, 158, 11, 0.1);
        border-color: #F59E0B;
        color: #FDE047;
    }
    
    .alert-success {
        background: rgba(16, 185, 129, 0.1);
        border-color: #10B981;
        color: #A7F3D0;
    }
    
    /* Header principal con título gradiente */
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        border-radius: 16px;
        padding: 30px 40px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    
    .gradient-text {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(to right, #60A5FA, #34D399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Estilos para pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        color: #94A3B8;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(59, 130, 246, 0.15) !important;
        border-color: #3B82F6 !important;
        color: #60A5FA !important;
    }
    </style>
    """,
    unsafe_allow_stdio=True,
    unsafe_allow_html=True
)

# Inicializar clases de lógica de negocio
doc_processor = DocumentProcessor()
twin_engine = DigitalTwinEngine(budget=200000000.0, total_days=730)
report_gen = LaTeXReportGenerator()
github_util = GitHubAutomation()

# Inicializar estados de la sesión de Streamlit para persistencia
if "metadata" not in st.session_state:
    st.session_state.metadata = {
        "budget": 200000000.0,
        "tunnel_length": 1450.0,
        "duration_days": 730,
        "geology": "Basaltos y coladas volcánicas (RMR medio de 60)",
        "water_table": "Nivel freático moderado (infiltración estimada < 20 L/min)"
    }

if "wbs_df" not in st.session_state:
    st.session_state.wbs_df = doc_processor.get_default_wbs()

if "actual_day" not in st.session_state:
    st.session_state.actual_day = 180

if "actual_cost" not in st.session_state:
    st.session_state.actual_cost = 45000000.0

if "actual_progress" not in st.session_state:
    st.session_state.actual_progress = 0.24 # 24% completado

# ================= SIDEBAR =================
st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2 style='color: #60A5FA; font-weight: 800; margin-bottom: 0;'>CIVIL-TWIN</h2>
        <span style='color: #94A3B8; font-size: 0.85rem; letter-spacing: 0.1em; text-transform: uppercase;'>Digital Twin Console</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("### 📊 Diario de Obra (Seguimiento)")
day_input = st.sidebar.number_input("Día de Control Actual", min_value=1, max_value=730, value=st.session_state.actual_day)
progress_pct = st.sidebar.slider("Avance Físico Real (%)", min_value=0.0, max_value=100.0, value=st.session_state.actual_progress * 100.0, step=0.1)
actual_cost_input = st.sidebar.number_input("Coste Real Incurrido (AC en €)", min_value=0.0, value=st.session_state.actual_cost, step=500000.0)

# Actualizar el estado global con las entradas de la barra lateral
st.session_state.actual_day = day_input
st.session_state.actual_progress = progress_pct / 100.0
st.session_state.actual_cost = actual_cost_input

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏔️ Parámetros del Frente de Túnel")
rmr_input = st.sidebar.slider("Calidad de Roca (RMR)", min_value=10, max_value=100, value=65)
depth_input = st.sidebar.slider("Profundidad de Excavación (m)", min_value=10, max_value=500, value=120)
water_input = st.sidebar.slider("Filtraciones de Agua (L/min)", min_value=0, max_value=150, value=15)

st.sidebar.markdown("---")
st.sidebar.info("🔒 **Seguridad Corporativa**: CIVIL-TWIN procesa y simula toda la información 100% de manera local en el navegador/servidor de la obra.")

# ================= ENCABEZADO DE LA APLICACIÓN =================
st.markdown(
    """
    <div class='main-header'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h1 style='color: white; margin: 0; font-weight: 800; font-size: 2.2rem;'>Gemelo Digital Fuerteventura</h1>
                <p style='color: #93C5FD; margin: 5px 0 0 0; font-size: 1.05rem;'>
                    Carretera Puerto del Rosario - Caldereta | Tramo Singulado de Carretera con Túnel de 1.45km
                </p>
            </div>
            <div style='text-align: right; background: rgba(255,255,255,0.1); padding: 10px 20px; border-radius: 8px;'>
                <span style='color: #93C5FD; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;'>Presupuesto Base (BAC)</span>
                <h2 style='color: #34D399; margin: 0; font-weight: 700;'>€200,000,000.00</h2>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ================= SECCIÓN DE DIAGNÓSTICO Y ALERTAS GENERALES =================
# Calcular EVM
metrics = twin_engine.calculate_evm(
    day=st.session_state.actual_day,
    actual_cost=st.session_state.actual_cost,
    actual_progress=st.session_state.actual_progress,
    tasks_df=st.session_state.wbs_df
)
alerts = twin_engine.get_alerts(metrics)

# Mostrar Banner de Alerta Principal
for alert in alerts:
    alert_type = alert["type"]
    if alert_type == "CRITICAL":
        st.markdown(f"<div class='alert-banner alert-critical'>⚠️ <b>[CRÍTICO]</b> {alert['message']}</div>", unsafe_allow_html=True)
    elif alert_type == "WARNING":
        st.markdown(f"<div class='alert-banner alert-warning'>🔔 <b>[ADVERTENCIA]</b> {alert['message']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='alert-banner alert-success'>✅ <b>[RENDIMIENTO ÓPTIMO]</b> {alert['message']}</div>", unsafe_allow_html=True)

# Pestañas principales
tab_dashboard, tab_document, tab_risk, tab_report, tab_saas = st.tabs([
    "📈 Cuadro de Mando y Gemelo Digital", 
    "📂 Ingestión Documental (NLP)", 
    "🔮 Simulación Geotécnica e IA", 
    "📄 LaTeX & Reportes Corporativos",
    "☁️ Repositorio y Despliegue SaaS"
])

# ================= TAB 1: CUADRO DE MANDO Y GEMELO DIGITAL =================
with tab_dashboard:
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cpi = metrics["CPI"]
        cpi_color = "#34D399" if cpi >= 1.0 else ("#F59E0B" if cpi >= 0.9 else "#EF4444")
        st.markdown(
            f"""
            <div class='kpi-card'>
                <div class='kpi-title'>CPI (Rendimiento Costes)</div>
                <div class='kpi-value' style='color: {cpi_color};'>{cpi:.3f}</div>
                <div style='color: #94A3B8; font-size: 0.8rem; margin-top: 5px;'>Avance logrado por euro gastado</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        spi = metrics["SPI"]
        spi_color = "#34D399" if spi >= 1.0 else ("#F59E0B" if spi >= 0.9 else "#EF4444")
        st.markdown(
            f"""
            <div class='kpi-card'>
                <div class='kpi-title'>SPI (Rendimiento Plazo)</div>
                <div class='kpi-value' style='color: {spi_color};'>{spi:.3f}</div>
                <div style='color: #94A3B8; font-size: 0.8rem; margin-top: 5px;'>Eficiencia frente al cronograma base</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col3:
        cv = metrics["CV"]
        cv_color = "#34D399" if cv >= 0.0 else "#EF4444"
        cv_sign = "+" if cv >= 0.0 else "-"
        st.markdown(
            f"""
            <div class='kpi-card'>
                <div class='kpi-title'>Cost Variance (CV)</div>
                <div class='kpi-value' style='color: {cv_color};'>{cv_sign}€{abs(cv):,.2f}</div>
                <div style='color: #94A3B8; font-size: 0.8rem; margin-top: 5px;'>Desviación económica neta</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col4:
        eac = metrics["EAC"]
        eac_color = "#34D399" if eac <= metrics["Budget"] else "#EF4444"
        st.markdown(
            f"""
            <div class='kpi-card'>
                <div class='kpi-title'>EAC (Coste Estimado Final)</div>
                <div class='kpi-value' style='color: {eac_color};'>€{eac:,.2f}</div>
                <div style='color: #94A3B8; font-size: 0.8rem; margin-top: 5px;'>Presupuesto final proyectado</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos e indicadores visuales
    col_chart, col_gantt = st.columns([3, 2])
    
    with col_chart:
        st.markdown("### 📊 Curva S del Gemelo Digital (Línea Base vs. Real)")
        
        # Simular curvas acumuladas a lo largo de 730 días
        days = np.arange(1, 731, 10)
        pv_curve = []
        for d in days:
            # Calcular PV para el día d
            val = 0.0
            for _, row in st.session_state.wbs_df.iterrows():
                start = row["Start_Day"]
                duration = row["Duration"]
                cost = row["Cost"]
                end = start + duration - 1
                if d > end:
                    val += cost
                elif d >= start:
                    val += ((d - start + 1) / duration) * cost
            pv_curve.append(val)
            
        # Curva de avance real acumulada hasta el día actual
        actual_days = [d for d in days if d <= st.session_state.actual_day]
        ac_curve = []
        ev_curve = []
        for i, d in enumerate(actual_days):
            # Progresión suave de progreso real
            fraction = d / st.session_state.actual_day
            ac_curve.append(st.session_state.actual_cost * fraction)
            ev_curve.append(metrics["EV"] * fraction)
            
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=pv_curve, name="Planned Value (Línea Base)", line=dict(color='#60A5FA', width=3)))
        fig.add_trace(go.Scatter(x=actual_days, y=ev_curve, name="Earned Value (Realizado)", line=dict(color='#34D399', width=3, dash='dash')))
        fig.add_trace(go.Scatter(x=actual_days, y=ac_curve, name="Actual Cost (Gastado)", line=dict(color='#EF4444', width=3)))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#E2E8F0',
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Días transcurridos"),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Presupuesto Acumulado (€)"),
            legend=dict(x=0.05, y=0.95),
            margin=dict(l=0, r=0, t=20, b=0),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col_gantt:
        st.markdown("### 📅 Cronograma Gantt de Actividades")
        # Generar Gantt interactivo
        df_gantt = st.session_state.wbs_df.copy()
        
        # Calcular fecha/día de fin de manera explícita
        df_gantt["End_Day"] = df_gantt["Start_Day"] + df_gantt["Duration"]
        
        fig_gantt = px.timeline(
            df_gantt, 
            x_start=df_gantt["Start_Day"].astype(str), # Convertir a strings/num para simular barras
            x_end=df_gantt["End_Day"].astype(str), 
            y="Task", 
            color="Duration",
            color_continuous_scale=px.colors.sequential.Bluyl,
            labels={"Task": "Actividad", "Duration": "Duración (Días)"}
        )
        
        fig_gantt.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#E2E8F0',
            yaxis=dict(autorange="reversed", gridcolor='rgba(255,255,255,0.05)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Línea de Tiempo del Proyecto (Días)"),
            margin=dict(l=0, r=0, t=20, b=0),
            height=400
        )
        st.plotly_chart(fig_gantt, use_container_width=True)

# ================= TAB 2: INGESTIÓN DOCUMENTAL (NLP) =================
with tab_document:
    st.markdown("### 📂 Ingestión de Documentos Técnicos y Gantt")
    st.markdown("Sube pliegos de condiciones técnicas (PDF) o planificaciones Gantt (CSV) para estructurar el gemelo digital en tiempo real.")
    
    col_upload_pdf, col_upload_csv = st.columns(2)
    
    with col_upload_pdf:
        st.markdown("#### 📄 Carga de Especificaciones Técnicas (PDF)")
        uploaded_pdf = st.file_uploader("Arrastra tu pliego técnico de carretera con túnel", type="pdf")
        if uploaded_pdf is not None:
            pdf_bytes = uploaded_pdf.read()
            # Ingestión con NLP local
            with st.spinner("Procesando PDF con técnicas de NLP locales..."):
                extracted_meta = doc_processor.parse_pdf(pdf_bytes)
                st.session_state.metadata.update(extracted_meta)
                st.success("✅ ¡PDF procesado e integrado exitosamente!")
                
        # Mostrar metadatos actuales del Gemelo
        st.markdown("##### 🔍 Variables Extraídas por la IA Local")
        meta = st.session_state.metadata
        st.markdown(f"- **Presupuesto (BAC):** €{meta['budget']:,.2f}")
        st.markdown(f"- **Longitud de Túnel:** {meta['tunnel_length']} metros")
        st.markdown(f"- **Plazo de Ejecución:** {meta['duration_days']} días")
        st.markdown(f"- **Geología Estimada:** {meta['geology']}")
        st.markdown(f"- **Filtro Freático:** {meta['water_table']}")
        
    with col_upload_csv:
        st.markdown("#### 📅 Importar Cronograma Gantt (CSV)")
        uploaded_csv = st.file_uploader("Carga tu archivo CSV de tareas Gantt", type="csv")
        if uploaded_csv is not None:
            csv_bytes = uploaded_csv.read()
            with st.spinner("Parseando estructura Gantt en local..."):
                df_parsed = doc_processor.parse_gantt_csv(csv_bytes)
                st.session_state.wbs_df = df_parsed
                st.success("✅ Estructura Gantt importada con éxito.")
                
        st.markdown("##### 🛠️ Estructura WBS de la Obra")
        st.dataframe(st.session_state.wbs_df, use_container_width=True)

# ================= TAB 3: SIMULACIÓN GEOTÉCNICA E IA =================
with tab_risk:
    st.markdown("### 🔮 Motor de Simulación y Análisis Predictivo de Riesgos")
    st.markdown(
        "Este módulo utiliza modelos de Machine Learning (Random Forest) entrenados con datasets de infraestructura reales "
        "y un simulador Monte Carlo para predecir escenarios probabilísticos de finalización."
    )
    
    col_sim_params, col_sim_chart = st.columns([1, 2])
    
    with col_sim_params:
        st.markdown("#### 🏔️ Diagnóstico del Frente de Excavación")
        st.write("Ajusta los parámetros geofísicos detectados para calcular el riesgo instantáneo del frente:")
        
        # Mostrar el nivel de riesgo predicho por el modelo en tiempo real
        risk_model = GeotechnicalRiskModel()
        risk_model.train() # Cargar/entrenar el clasificador local
        
        risk_class = risk_model.predict([[rmr_input, depth_input, water_input]])[0]
        risk_probs = risk_model.predict_proba([[rmr_input, depth_input, water_input]])[0]
        
        risk_levels = ["BAJO", "MEDIO", "ALTO"]
        risk_colors = ["#34D399", "#F59E0B", "#EF4444"]
        
        st.markdown(
            f"""
            <div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; text-align: center;'>
                <span style='color: #94A3B8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;'>Clasificación Geotécnica IA</span>
                <h1 style='color: {risk_colors[risk_class]}; font-weight: 800; margin: 5px 0;'>RIESGO {risk_levels[risk_class]}</h1>
                <div style='display: flex; justify-content: space-around; margin-top: 15px;'>
                    <div><span style='font-size:0.8rem; color:#94A3B8;'>Bajo</span><br><b style='color:#34D399;'>{risk_probs[0]*100:.0f}%</b></div>
                    <div><span style='font-size:0.8rem; color:#94A3B8;'>Medio</span><br><b style='color:#F59E0B;'>{risk_probs[1]*100:.0f}%</b></div>
                    <div><span style='font-size:0.8rem; color:#94A3B8;'>Alto</span><br><b style='color:#EF4444;'>{risk_probs[2]*100:.0f}%</b></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Ejecutar Simulación Monte Carlo interactiva
        st.markdown("#### ⚡ Simulación de Monte Carlo")
        sim_iterations = st.slider("Iteraciones", min_value=100, max_value=5000, value=2000, step=100)
        run_sim = st.button("🚀 Iniciar Simulación Probabilística")
        
    with col_sim_chart:
        # Ejecutar Monte Carlo
        mc_simulator = MonteCarloSimulator()
        sim_results = mc_simulator.run_simulation(
            tasks_df=st.session_state.wbs_df, 
            rmr=rmr_input, 
            water_influx=water_input, 
            depth=depth_input, 
            iterations=sim_iterations
        )
        
        st.markdown("#### 📈 Distribución Probabilística de Costes Finales")
        
        # Graficar histograma de costes con Plotly
        fig_mc_cost = px.histogram(
            x=sim_results["costs"] / 1000000.0, 
            nbins=50, 
            color_discrete_sequence=['#3B82F6'],
            labels={"x": "Coste Final del Proyecto (Millones de Euros)", "y": "Frecuencia de Ocurrencias"}
        )
        # Añadir líneas de percentiles
        fig_mc_cost.add_vline(x=sim_results["p10_cost"] / 1000000.0, line_dash="dash", line_color="#34D399", 
                              annotation_text=f"P10 (Optimista): €{sim_results['p10_cost']/1000000.0:.1f}M")
        fig_mc_cost.add_vline(x=sim_results["p50_cost"] / 1000000.0, line_color="#F59E0B", 
                              annotation_text=f"P50 (Probable): €{sim_results['p50_cost']/1000000.0:.1f}M")
        fig_mc_cost.add_vline(x=sim_results["p90_cost"] / 1000000.0, line_dash="dash", line_color="#EF4444", 
                              annotation_text=f"P90 (Pesimista): €{sim_results['p90_cost']/1000000.0:.1f}M")
        
        fig_mc_cost.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#E2E8F0',
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            margin=dict(l=0, r=0, t=30, b=0),
            height=300
        )
        st.plotly_chart(fig_mc_cost, use_container_width=True)
        
        # Resultados Resumidos
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric("P10 Duración (Plazo Corto)", f"{sim_results['p10_duration']} días")
        with col_res2:
            st.metric("P50 Duración (Plazo Medio)", f"{sim_results['p50_duration']} días")
        with col_res3:
            st.metric("P90 Duración (Plazo con Riesgo)", f"{sim_results['p90_duration']} días")

# ================= TAB 4: LATEX & REPORTES CORPORATIVOS =================
with tab_report:
    st.markdown("### 📄 Informes Ejecutivos en LaTeX")
    st.markdown(
        "CIVIL-TWIN automatiza la redacción técnica estructurada para la junta de dirección de obra. "
        "El código es 100% estándar de LaTeX y puede copiarse directamente o compilarse en PDF."
    )
    
    # Generar LaTeX dinámico
    risk_results = {
        "p50_duration": sim_results["p50_duration"],
        "p90_duration": sim_results["p90_duration"],
        "p50_cost": sim_results["p50_cost"],
        "p90_cost": sim_results["p90_cost"],
        "geotechnical_risk_level": risk_class
    }
    
    latex_code = report_gen.generate_report(
        metadata=st.session_state.metadata,
        evm_metrics=metrics,
        risk_results=risk_results
    )
    
    # Botón de Descarga
    st.download_button(
        label="📥 Descargar Código LaTeX (.tex)",
        data=latex_code,
        file_name=f"informe_obra_dia_{st.session_state.actual_day}.tex",
        mime="text/plain"
    )
    
    col_code, col_preview = st.columns([1, 1])
    
    with col_code:
        st.markdown("#### 💻 Editor / Código LaTeX Generado")
        edited_latex = st.text_area("Código fuente LaTeX listo para compilar", value=latex_code, height=450)
        
    with col_preview:
        st.markdown("#### 👁️ Previsualización del Informe Estructurado")
        # Mostrar estructura bonita en markdown simulando el PDF renderizado de LaTeX
        st.markdown(
            f"""
            <div style='background: white; color: #333; padding: 30px; border-radius: 12px; height: 450px; overflow-y: scroll; box-shadow: inset 0 2px 10px rgba(0,0,0,0.1); font-family: serif;'>
                <div style='text-align: center; border-bottom: 2px solid #1A365D; padding-bottom: 10px;'>
                    <h2 style='color: #1A365D; font-weight: 800; font-size: 1.5rem; margin: 0;'>INFORME EJECUTIVO DE CONTROL DE OBRA</h2>
                    <span style='font-size: 0.9rem; color: #555;'>Carretera Puerto del Rosario - Caldereta | Tramo Singulado</span>
                </div>
                <br>
                <h4 style='color: #1A365D;'>1. Resumen del Proyecto e Ingestión Documental</h4>
                <p style='font-size: 0.9rem;'>Este informe técnico ha sido generado automáticamente por el Gemelo Digital <b>CIVIL-TWIN</b> en base a los datos extraídos de los pliegos técnicos y el diario de obra procesados localmente mediante técnicas de NLP.</p>
                <ul>
                    <li style='font-size: 0.9rem;'><b>Presupuesto Base (BAC):</b> €{st.session_state.metadata['budget']:,.2f}</li>
                    <li style='font-size: 0.9rem;'><b>Longitud de Túnel:</b> {st.session_state.metadata['tunnel_length']} metros</li>
                    <li style='font-size: 0.9rem;'><b>Geología:</b> {st.session_state.metadata['geology']}</li>
                </ul>
                
                <h4 style='color: #1A365D;'>2. Análisis del Valor Ganado (EVM) - Día {st.session_state.actual_day}</h4>
                <table style='width: 100%; font-size: 0.8rem; border-collapse: collapse;'>
                    <tr style='background: #f2f2f2; border-bottom: 1px solid #ddd;'>
                        <th style='padding: 5px; text-align: left;'>Métrica de Control</th>
                        <th style='padding: 5px; text-align: right;'>Valor (€ / Ratio)</th>
                    </tr>
                    <tr><td style='padding: 3px;'>Valor Planificado (PV)</td><td style='padding: 3px; text-align: right;'>€{metrics['PV']:,.2f}</td></tr>
                    <tr><td style='padding: 3px;'>Valor Ganado (EV)</td><td style='padding: 3px; text-align: right;'>€{metrics['EV']:,.2f}</td></tr>
                    <tr><td style='padding: 3px;'>Coste Real (AC)</td><td style='padding: 3px; text-align: right;'>€{metrics['AC']:,.2f}</td></tr>
                    <tr style='font-weight: bold; border-top: 1px solid #1A365D;'><td style='padding: 3px;'>CPI</td><td style='padding: 3px; text-align: right;'>{metrics['CPI']:.3f}</td></tr>
                    <tr style='font-weight: bold;'><td style='padding: 3px;'>SPI</td><td style='padding: 3px; text-align: right;'>{metrics['SPI']:.3f}</td></tr>
                </table>
                
                <h4 style='color: #1A365D;'>3. Simulación de Monte Carlo e IA</h4>
                <ul>
                    <li style='font-size: 0.9rem;'><b>Nivel de Riesgo del Frente:</b> <span style='color: {risk_colors[risk_class]}; font-weight: bold;'>{risk_levels[risk_class]}</span></li>
                    <li style='font-size: 0.9rem;'><b>Finalización Probable (P50):</b> {sim_results['p50_duration']} días (Desviación: {sim_results['p50_duration'] - st.session_state.metadata['duration_days']} días)</li>
                    <li style='font-size: 0.9rem;'><b>Costo Final Probable (P50):</b> €{sim_results['p50_cost']:,.2f}</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

# ================= TAB 5: REPOSITORIO Y DESPLIEGUE SAAS =================
with tab_saas:
    st.markdown("### ☁️ Gestión del Repositorio y Despliegue SaaS")
    st.markdown(
        "CIVIL-TWIN permite automatizar la inicialización del repositorio Git local, configurar las "
        "herramientas CI/CD e infraestructura en Docker, y proveer accesos instantáneos para pruebas en la nube."
    )
    
    col_git, col_saas_link = st.columns(2)
    
    with col_git:
        st.markdown("#### 🛠️ Inicializar Repositorio Git Local")
        st.write("Genera y actualiza archivos de infraestructura (Dockerfile, docker-compose.yml, workflows de CI/CD de GitHub Actions, README.md):")
        
        if st.button("🔧 Generar e Inicializar Repositorio"):
            res = github_util.init_local_repo()
            if res:
                st.success("✅ ¡Infraestructura de desarrollo inicializada y confirmada en Git!")
                st.info("Archivos creados: README.md, Dockerfile, docker-compose.yml, .github/workflows/test.yml y requirements.txt")
            else:
                st.error("❌ Error al inicializar Git.")
                
        # Consola de instrucciones
        instructions = github_util.prepare_saas_deployment()
        st.markdown("##### 💻 Instrucciones para empujar a GitHub corporativo")
        st.code(instructions["github_instructions"], language="bash")
        
    with col_saas_link:
        st.markdown("#### 🚀 Acceso SaaS para el Gerente (Demo Cloud)")
        st.write(
            "Para que el gerente pruebe de manera remota e interactiva el Gemelo Digital MVP sin necesidad "
            "de instalaciones complejas, CIVIL-TWIN está preparado para desplegarse mediante un solo enlace:"
        )
        
        # Enlaces interactivos
        st.markdown(
            f"""
            <div style='background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); padding: 25px; border-radius: 12px; margin-top: 15px;'>
                <h4 style='color: #60A5FA; margin-top:0;'>🔗 Enlace Demo SaaS Generado</h4>
                <p style='font-size: 0.9rem;'>Haz clic para simular la demo interactiva en la nube o configurar el despliegue automático:</p>
                <a href='{instructions["streamlit_cloud_link"]}' target='_blank' style='display: inline-block; background: #2563EB; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-right:10px;'>🚀 Streamlit Cloud Demo</a>
                <a href='{instructions["huggingface_spaces_link"]}' target='_blank' style='display: inline-block; background: #4B5563; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold;'>🤗 Hugging Face Spaces</a>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning(f"🔒 {instructions['enterprise_safety']}")
