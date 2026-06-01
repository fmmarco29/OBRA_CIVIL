import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import requests

from src.document_processor import DocumentProcessor
from src.digital_twin import DigitalTwinEngine
from src.report_generator import LaTeXReportGenerator
from src.github_automation import GitHubAutomation

import os
# Resolver dinamicamente la URL del backend para maxima resiliencia
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

# Probar la conexion y reasignar si es necesario
if "backend_url_resolved" not in st.session_state:
    st.session_state.backend_url_resolved = BACKEND_URL
    for url in [BACKEND_URL, "http://localhost:8000", "http://127.0.0.1:8000", "http://api:8000"]:
        try:
            r = requests.get(url + "/", timeout=1.0)
            if r.status_code == 200:
                st.session_state.backend_url_resolved = url
                break
        except Exception:
            pass

BACKEND_URL = st.session_state.backend_url_resolved

st.set_page_config(
    page_title="CIVIL-TWIN | B2B Enterprise Digital Twin",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilizacion premium con inyeccion de CSS estilo Glassmorphism y Dark Mode Tailored
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(20, 24, 43, 1) 0%, rgba(8, 10, 15, 1) 100%);
        color: #E2E8F0;
    }
    
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
    
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        border-radius: 16px;
        padding: 30px 40px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    
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
    unsafe_allow_html=True
)

# Inicializar clases de logica de negocio locales
doc_processor = DocumentProcessor()
twin_engine = DigitalTwinEngine(budget=200000000.0, total_days=730)
report_gen = LaTeXReportGenerator()
github_util = GitHubAutomation()

# Inicializar estados de la sesion de Streamlit para persistencia
if "metadata" not in st.session_state:
    st.session_state.metadata = {
        "budget": 200000000.0,
        "tunnel_length": 1450.0,
        "duration_days": 730,
        "geology": "Basaltos y coladas volcanicas (RMR medio de 60)",
        "water_table": "Nivel freatico moderado (infiltracion estimada < 20 L/min)"
    }

if "wbs_df" not in st.session_state:
    st.session_state.wbs_df = doc_processor.get_default_wbs()

if "actual_day" not in st.session_state:
    st.session_state.actual_day = 180

if "actual_cost" not in st.session_state:
    st.session_state.actual_cost = 45000000.0

if "actual_progress" not in st.session_state:
    st.session_state.actual_progress = 0.24

if "tenant_token" not in st.session_state:
    st.session_state.tenant_token = "token_fuerteventura_enterprise"

if "tenant_info" not in st.session_state:
    st.session_state.tenant_info = None

if "tenant_projects" not in st.session_state:
    st.session_state.tenant_projects = []

if "sim_results" not in st.session_state:
    st.session_state.sim_results = None

# ================= SIDEBAR =================
st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2 style='color: #60A5FA; font-weight: 800; margin-bottom: 0;'>CIVIL-TWIN SaaS</h2>
        <span style='color: #94A3B8; font-size: 0.85rem; letter-spacing: 0.1em; text-transform: uppercase;'>Consola Gemelo Digital</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("### Credenciales de Acceso")
token_input = st.sidebar.text_input("B2B Tenant Token", value=st.session_state.tenant_token, type="password")
if token_input != st.session_state.tenant_token:
    st.session_state.tenant_token = token_input
    st.session_state.tenant_info = None
    st.session_state.tenant_projects = []

# Consultar Tenant Info si no esta cargado
if st.session_state.tenant_token and st.session_state.tenant_info is None:
    try:
        headers = {"Authorization": f"Bearer {st.session_state.tenant_token}"}
        proj_res = requests.get(f"{BACKEND_URL}/tenant/projects", headers=headers)
        if proj_res.status_code == 200:
            st.session_state.tenant_projects = proj_res.json()
            # Simulamos obtener info del tenant
            if "fuerteventura" in st.session_state.tenant_token:
                st.session_state.tenant_info = {"name": "Fuerteventura Civil S.A.", "tier": "Enterprise"}
            elif "agaete" in st.session_state.tenant_token:
                st.session_state.tenant_info = {"name": "Consorcio Vial Agaete", "tier": "Premium"}
            else:
                st.session_state.tenant_info = {"name": "Tenant Generico", "tier": "Standard"}
        else:
            st.sidebar.error("Token no autorizado o backend inactivo")
    except Exception:
        # Fallback local silencioso si el backend no esta encendido
        pass

if st.session_state.tenant_info:
    st.sidebar.success(f"Tenant: {st.session_state.tenant_info['name']} ({st.session_state.tenant_info['tier']})")
else:
    st.sidebar.warning("Conectado en modo Offline (Sin Backend)")

st.sidebar.markdown("### Diario de Obra (Seguimiento)")
day_input = st.sidebar.number_input("Dia de Control Actual", min_value=1, max_value=730, value=st.session_state.actual_day)
progress_pct = st.sidebar.slider("Avance Fisico Real (%)", min_value=0.0, max_value=100.0, value=st.session_state.actual_progress * 100.0, step=0.1)
actual_cost_input = st.sidebar.number_input("Coste Real Incurrido (AC en Euros)", min_value=0.0, value=st.session_state.actual_cost, step=500000.0)

# Actualizar el estado global
st.session_state.actual_day = day_input
st.session_state.actual_progress = progress_pct / 100.0
st.session_state.actual_cost = actual_cost_input

st.sidebar.markdown("---")
st.sidebar.markdown("### Parametros del Frente de Tunel")
rmr_input = st.sidebar.slider("Calidad de Roca (RMR)", min_value=10, max_value=100, value=65)
depth_input = st.sidebar.slider("Profundidad de Excavacion (m)", min_value=10, max_value=500, value=120)
water_input = st.sidebar.slider("Filtraciones de Agua (L/min)", min_value=0, max_value=150, value=15)

st.sidebar.markdown("---")
st.sidebar.info("CIVIL-TWIN B2B SaaS: Procesamiento pesado delegado a clusters de calculo asincronos FastAPI externos de grado empresarial.")

# ================= ENCABEZADO DE LA APLICACION =================
st.markdown(
    """
    <div class='main-header'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h1 style='color: white; margin: 0; font-weight: 800; font-size: 2.2rem;'>Gemelo Digital Fuerteventura</h1>
                <p style='color: #93C5FD; margin: 5px 0 0 0; font-size: 1.05rem;'>
                    Carretera Puerto del Rosario - Caldereta | SaaS Decoupled Enterprise Edition
                </p>
            </div>
            <div style='text-align: right; background: rgba(255,255,255,0.1); padding: 10px 20px; border-radius: 8px;'>
                <span style='color: #93C5FD; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;'>Presupuesto Base (BAC)</span>
                <h2 style='color: #34D399; margin: 0; font-weight: 700;'>200,000,000.00 Euros</h2>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Calcular EVM localmente
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
        st.markdown(f"<div class='alert-banner alert-critical'>[CRITICO] {alert['message']}</div>", unsafe_allow_html=True)
    elif alert_type == "WARNING":
        st.markdown(f"<div class='alert-banner alert-warning'>[ADVERTENCIA] {alert['message']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='alert-banner alert-success'>[ESTABLE] {alert['message']}</div>", unsafe_allow_html=True)

# Pestañas principales
tab_dashboard, tab_document, tab_risk, tab_report, tab_saas = st.tabs([
    "Cuadro de Mando y Gemelo Digital", 
    "Ingestion Documental y Graph RAG", 
    "Simulacion Geotecnica e IA API", 
    "LaTeX & Reportes Corporativos",
    "Consola de Tenant & SaaS B2B"
])

# ================= TAB 1: CUADRO DE MANDO Y GEMELO DIGITAL =================
with tab_dashboard:
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
                <div class='kpi-value' style='color: {cv_color};'>{cv_sign}Euro{abs(cv):,.2f}</div>
                <div style='color: #94A3B8; font-size: 0.8rem; margin-top: 5px;'>Desviacion economica neta</div>
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
                <div class='kpi-value' style='color: {eac_color};'>Euro{eac:,.2f}</div>
                <div style='color: #94A3B8; font-size: 0.8rem; margin-top: 5px;'>Presupuesto final proyectado</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_chart, col_gantt = st.columns([3, 2])
    
    with col_chart:
        st.markdown("### Curva S del Gemelo Digital (Linea Base vs. Real)")
        
        days = np.arange(1, 731, 10)
        pv_curve = []
        for d in days:
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
            
        actual_days = [d for d in days if d <= st.session_state.actual_day]
        ac_curve = []
        ev_curve = []
        for i, d in enumerate(actual_days):
            fraction = d / st.session_state.actual_day
            ac_curve.append(st.session_state.actual_cost * fraction)
            ev_curve.append(metrics["EV"] * fraction)
            
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=pv_curve, name="Planned Value (Linea Base)", line=dict(color='#60A5FA', width=3)))
        fig.add_trace(go.Scatter(x=actual_days, y=ev_curve, name="Earned Value (Realizado)", line=dict(color='#34D399', width=3, dash='dash')))
        fig.add_trace(go.Scatter(x=actual_days, y=ac_curve, name="Actual Cost (Gastado)", line=dict(color='#EF4444', width=3)))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#E2E8F0',
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Dias transcurridos"),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Presupuesto Acumulado (Euro)"),
            legend=dict(x=0.05, y=0.95),
            margin=dict(l=0, r=0, t=20, b=0),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col_gantt:
        st.markdown("### Cronograma Gantt de Actividades")
        df_gantt = st.session_state.wbs_df.copy()
        df_gantt["End_Day"] = df_gantt["Start_Day"] + df_gantt["Duration"]
        
        fig_gantt = px.timeline(
            df_gantt, 
            x_start=df_gantt["Start_Day"].astype(str),
            x_end=df_gantt["End_Day"].astype(str), 
            y="Task", 
            color="Duration",
            color_continuous_scale=px.colors.sequential.Bluyl,
            labels={"Task": "Actividad", "Duration": "Duracion (Dias)"}
        )
        
        fig_gantt.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#E2E8F0',
            yaxis=dict(autorange="reversed", gridcolor='rgba(255,255,255,0.05)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Linea de Tiempo del Proyecto (Dias)"),
            margin=dict(l=0, r=0, t=20, b=0),
            height=400
        )
        st.plotly_chart(fig_gantt, use_container_width=True)

# ================= TAB 2: INGESTION DOCUMENTAL Y GRAPH RAG =================
with tab_document:
    st.markdown("### Ingestion de Especificaciones Tecnicas e Indexacion en Graph RAG")
    st.markdown("Sube pliegos de condiciones tecnicas de obra civil (ej. Carretera El Risco-Agaete) para mapear entidades en el Grafo de Conocimiento corporativo.")
    
    col_upload_pdf, col_upload_csv = st.columns(2)
    
    with col_upload_pdf:
        st.markdown("#### Carga de Especificaciones Tecnicas y Gantt (PDF)")
        uploaded_pdf = st.file_uploader("Arrastra tu pliego tecnico de carretera con tunel", type="pdf")
        
        pdf_content_str = ""
        if uploaded_pdf is not None:
            pdf_bytes = uploaded_pdf.read()
            with st.spinner("Procesando PDF con tecnicas de NLP locales..."):
                extracted_meta = doc_processor.parse_pdf(pdf_bytes)
                st.session_state.metadata.update(extracted_meta)
                st.success("PDF procesado localmente.")
                pdf_content_str = "Especificacion de la Carretera Fuerteventura con tunel de 1450m y geologia volcanica."
                
            st.markdown("##### Convertidor Inteligente a Microsoft Project")
            st.write("Extrae la WBS planificada del PDF y genera un archivo de planificacion compatible con MS Project:")
            if st.button("Extraer WBS y Generar MS Project (.xml)"):
                with st.spinner("Analizando estructuras y dependencias del pliego..."):
                    df_pdf = doc_processor.parse_pdf_to_wbs(pdf_bytes)
                    st.session_state.wbs_df = df_pdf
                    st.success("WBS de obra civil extraida del PDF con éxito.")
            
            xml_data = doc_processor.generate_project_xml(st.session_state.wbs_df)
            st.download_button(
                label="Descargar Planificacion para MS Project (.xml)",
                data=xml_data,
                file_name="planificacion_desde_pdf.xml",
                mime="text/xml"
            )
                
        st.markdown("##### Variables Extraidas por la IA Local")
        meta = st.session_state.metadata
        st.markdown(f"- **Presupuesto (BAC):** Euro{meta['budget']:,.2f}")
        st.markdown(f"- **Longitud de Tunel:** {meta['tunnel_length']} metros")
        st.markdown(f"- **Plazo de Ejecucion:** {meta['duration_days']} dias")
        st.markdown(f"- **Geologia Estimada:** {meta['geology']}")
        st.markdown(f"- **Filtro Freatico:** {meta['water_table']}")
        
        if pdf_content_str:
            st.markdown("#### Sincronizar con Knowledge Graph RAG (Backend)")
            if st.button("Enviar e Indexar en el Grafo de Conocimiento"):
                payload = {
                    "document_name": uploaded_pdf.name,
                    "content": pdf_content_str,
                    "metadata": {"project_id": "proj_fv_001"}
                }
                try:
                    res = requests.post(f"{BACKEND_URL}/rag/ingest", json=payload)
                    if res.status_code == 200:
                        st.success("Documento indexado con exito en el backend Graph RAG.")
                        st.json(res.json()["extracted_subgraph"])
                    else:
                        st.error("Error al indexar en el Grafo de Conocimiento.")
                except Exception as e:
                    st.error(f"No se pudo conectar con el backend de Grafos: {str(e)}")
        
    with col_upload_csv:
        st.markdown("#### Importar Cronograma (CSV o XML de MS Project)")
        uploaded_file = st.file_uploader("Carga tu planificacion (CSV o XML de MS Project)", type=["csv", "xml"])
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            with st.spinner("Parseando planificacion en local..."):
                if uploaded_file.name.endswith(".xml"):
                    df_parsed = doc_processor.parse_project_xml(file_bytes)
                    st.session_state.wbs_df = df_parsed
                    st.success("Cronograma XML de MS Project importado con exito.")
                else:
                    df_parsed = doc_processor.parse_gantt_csv(file_bytes)
                    st.session_state.wbs_df = df_parsed
                    st.success("Cronograma CSV importado con exito.")
                
        st.markdown("##### Estructura WBS de la Obra")
        st.dataframe(st.session_state.wbs_df, use_container_width=True)

# ================= TAB 3: SIMULACION GEOTECNICA E IA API =================
with tab_risk:
    st.markdown("### Motor de Simulacion y Analisis Predictivo de Riesgos asincrono")
    st.markdown(
        "Este modulo realiza llamadas al backend asincrono de FastAPI que ejecuta simulaciones de Monte Carlo "
        "optimizadas mediante calculo vectorial en NumPy y prediccion mediante Random Forest."
    )
    
    col_sim_params, col_sim_chart = st.columns([1, 2])
    
    with col_sim_params:
        st.markdown("#### Diagnostico del Frente de Excavacion")
        st.write("Ajusta los parametros geofisicos detectados para calcular el riesgo del frente a traves de la API:")
        
        # Simular clasificacion geotecnica llamando de forma asincrona o estimacion local rapida si offline
        risk_class = 0
        risk_probs = [0.8, 0.15, 0.05]
        
        # Realizamos llamada de simulacion si esta activo
        sim_iterations = st.slider("Iteraciones", min_value=100, max_value=5000, value=2000, step=100)
        run_sim = st.button("Iniciar Simulacion en API Backend")
        
    with col_sim_chart:
        # Peticion de simulacion al backend
        tasks_list = []
        for idx, r in st.session_state.wbs_df.iterrows():
            tasks_list.append({
                "Task_ID": int(r["Task_ID"]),
                "Task": str(r["Task"]),
                "Duration": float(r["Duration"]),
                "Cost": float(r["Cost"]),
                "Start_Day": int(r["Start_Day"]),
                "Predecessors": str(r["Predecessors"]) if pd.notna(r["Predecessors"]) else ""
            })
            
        payload = {
            "tasks": tasks_list,
            "rmr": float(rmr_input),
            "water_influx": float(water_input),
            "depth": float(depth_input),
            "iterations": int(sim_iterations)
        }
        
        # Ejecutar peticion
        backend_active = False
        try:
            res = requests.post(f"{BACKEND_URL}/simulate/montecarlo", json=payload)
            if res.status_code == 200:
                st.session_state.sim_results = res.json()
                backend_active = True
            else:
                st.error("Error al procesar la simulacion en el backend.")
        except Exception:
            pass
            
        # Si fallase la comunicacion con el backend, realizamos una generacion de simulacion sintetica de reserva
        if st.session_state.sim_results is None or not backend_active:
            st.warning("Usando simulador local de reserva (Backend inactivo o no disponible)")
            # Simular de forma basica local
            np.random.seed(42)
            sim_costs_fallback = np.random.normal(205000000.0, 15000000.0, sim_iterations)
            sim_durations_fallback = np.random.normal(750, 45, sim_iterations)
            st.session_state.sim_results = {
                "costs": sim_costs_fallback.tolist(),
                "durations": sim_durations_fallback.tolist(),
                "p10_duration": int(np.percentile(sim_durations_fallback, 10)),
                "p50_duration": int(np.percentile(sim_durations_fallback, 50)),
                "p90_duration": int(np.percentile(sim_durations_fallback, 90)),
                "p10_cost": float(np.percentile(sim_costs_fallback, 10)),
                "p50_cost": float(np.percentile(sim_costs_fallback, 50)),
                "p90_cost": float(np.percentile(sim_costs_fallback, 90)),
                "geotechnical_risk_level": 1
            }

        sim_results = st.session_state.sim_results
        
        # Mapeo de riesgos
        risk_levels = ["BAJO", "MEDIO", "ALTO"]
        risk_colors = ["#34D399", "#F59E0B", "#EF4444"]
        risk_class = sim_results.get("geotechnical_risk_level", 0)
        
        st.markdown(
            f"""
            <div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 20px;'>
                <span style='color: #94A3B8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;'>Estado Geotecnico API</span>
                <h2 style='color: {risk_colors[risk_class]}; font-weight: 800; margin: 5px 0;'>RIESGO {risk_levels[risk_class]}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("#### Distribucion Probabilistica de Costes Finales (Monte Carlo)")
        
        costs_array = np.array(sim_results["costs"])
        fig_mc_cost = px.histogram(
            x=costs_array / 1000000.0, 
            nbins=50, 
            color_discrete_sequence=['#3B82F6'],
            labels={"x": "Coste Final del Proyecto (Millones de Euros)", "y": "Frecuencia de Ocurrencias"}
        )
        fig_mc_cost.add_vline(x=sim_results["p10_cost"] / 1000000.0, line_dash="dash", line_color="#34D399", 
                               annotation_text=f"P10: Euro{sim_results['p10_cost']/1000000.0:.1f}M")
        fig_mc_cost.add_vline(x=sim_results["p50_cost"] / 1000000.0, line_color="#F59E0B", 
                               annotation_text=f"P50: Euro{sim_results['p50_cost']/1000000.0:.1f}M")
        fig_mc_cost.add_vline(x=sim_results["p90_cost"] / 1000000.0, line_dash="dash", line_color="#EF4444", 
                               annotation_text=f"P90: Euro{sim_results['p90_cost']/1000000.0:.1f}M")
        
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
        
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric("P10 Duracion (Plazo Corto)", f"{sim_results['p10_duration']} dias")
        with col_res2:
            st.metric("P50 Duracion (Plazo Medio)", f"{sim_results['p50_duration']} dias")
        with col_res3:
            st.metric("P90 Duracion (Plazo con Riesgo)", f"{sim_results['p90_duration']} dias")

# ================= TAB 4: LATEX & REPORTES CORPORATIVOS =================
with tab_report:
    st.markdown("### Informes Ejecutivos en LaTeX")
    st.markdown(
        "CIVIL-TWIN automatiza la redaccion tecnica estructurada para la junta de direccion de obra. "
        "El codigo es 100% estandar de LaTeX y puede copiarse directamente o descargarse."
    )
    
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
    
    st.download_button(
        label="Descargar Codigo LaTeX (.tex)",
        data=latex_code,
        file_name=f"informe_obra_dia_{st.session_state.actual_day}.tex",
        mime="text/plain"
    )
    
    col_code, col_preview = st.columns([1, 1])
    
    with col_code:
        st.markdown("#### Editor / Codigo LaTeX Generado")
        edited_latex = st.text_area("Codigo fuente LaTeX listo para compilar", value=latex_code, height=450)
        
    with col_preview:
        st.markdown("#### Previsualizacion del Informe Estructurado")
        st.markdown(
            f"""
            <div style='background: white; color: #333; padding: 30px; border-radius: 12px; height: 450px; overflow-y: scroll; box-shadow: inset 0 2px 10px rgba(0,0,0,0.1); font-family: serif;'>
                <div style='text-align: center; border-bottom: 2px solid #1A365D; padding-bottom: 10px;'>
                    <h2 style='color: #1A365D; font-weight: 800; font-size: 1.5rem; margin: 0;'>INFORME EJECUTIVO DE CONTROL DE OBRA</h2>
                    <span style='font-size: 0.9rem; color: #555;'>Carretera Puerto del Rosario - Caldereta | Tramo Singulado</span>
                </div>
                <br>
                <h4 style='color: #1A365D;'>1. Resumen del Proyecto e Ingestion Documental</h4>
                <p style='font-size: 0.9rem;'>Este informe tecnico ha sido generado automaticamente por el Gemelo Digital <b>CIVIL-TWIN</b> en base a los datos extraidos de los pliegos tecnicos y el diario de obra procesados localmente mediante tecnicas de NLP.</p>
                <ul>
                    <li style='font-size: 0.9rem;'><b>Presupuesto Base (BAC):</b> Euro{st.session_state.metadata['budget']:,.2f}</li>
                    <li style='font-size: 0.9rem;'><b>Longitud de Tunel:</b> {st.session_state.metadata['tunnel_length']} metros</li>
                    <li style='font-size: 0.9rem;'><b>Geologia:</b> {st.session_state.metadata['geology']}</li>
                </ul>
                
                <h4 style='color: #1A365D;'>2. Analisis del Valor Ganado (EVM) - Dia {st.session_state.actual_day}</h4>
                <table style='width: 100%; font-size: 0.8rem; border-collapse: collapse;'>
                    <tr style='background: #f2f2f2; border-bottom: 1px solid #ddd;'>
                        <th style='padding: 5px; text-align: left;'>Metrica de Control</th>
                        <th style='padding: 5px; text-align: right;'>Valor (Euro / Ratio)</th>
                    </tr>
                    <tr><td style='padding: 3px;'>Valor Planificado (PV)</td><td style='padding: 3px; text-align: right;'>Euro{metrics['PV']:,.2f}</td></tr>
                    <tr><td style='padding: 3px;'>Valor Ganado (EV)</td><td style='padding: 3px; text-align: right;'>Euro{metrics['EV']:,.2f}</td></tr>
                    <tr><td style='padding: 3px;'>Coste Real (AC)</td><td style='padding: 3px; text-align: right;'>Euro{metrics['AC']:,.2f}</td></tr>
                    <tr style='font-weight: bold; border-top: 1px solid #1A365D;'><td style='padding: 3px;'>CPI</td><td style='padding: 3px; text-align: right;'>{metrics['CPI']:.3f}</td></tr>
                    <tr style='font-weight: bold;'><td style='padding: 3px;'>SPI</td><td style='padding: 3px; text-align: right;'>{metrics['SPI']:.3f}</td></tr>
                </table>
                
                <h4 style='color: #1A365D;'>3. Simulacion de Monte Carlo e IA</h4>
                <ul>
                    <li style='font-size: 0.9rem;'><b>Nivel de Riesgo del Frente:</b> <span style='color: {risk_colors[risk_class]}; font-weight: bold;'>{risk_levels[risk_class]}</span></li>
                    <li style='font-size: 0.9rem;'><b>Finalizacion Probable (P50):</b> {sim_results['p50_duration']} dias (Desviacion: {sim_results['p50_duration'] - st.session_state.metadata['duration_days']} dias)</li>
                    <li style='font-size: 0.9rem;'><b>Costo Final Probable (P50):</b> Euro{sim_results['p50_cost']:,.2f}</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

# ================= TAB 5: CONSOLA DE TENANT & SAAS B2B =================
with tab_saas:
    st.markdown("### Consola de Administracion SaaS B2B Multi-Tenant")
    st.markdown("Gestión y auditoría del estado del tenant en la arquitectura multinivel y despliegue del cluster.")
    
    col_git, col_saas_link = st.columns(2)
    
    with col_git:
        st.markdown("#### Datos de la Suscripción Tenant")
        if st.session_state.tenant_info:
            st.info(f"Organizacion: {st.session_state.tenant_info['name']}")
            st.info(f"Nivel de Servicio (Tier): {st.session_state.tenant_info['tier']}")
            
            st.markdown("##### Proyectos Asignados a este Tenant:")
            if st.session_state.tenant_projects:
                for proj in st.session_state.tenant_projects:
                    st.write(f"- **[{proj['project_id']}]** {proj['name']} (Estado: {proj['status'].upper()})")
            else:
                st.write("No se encontraron proyectos activos vinculados.")
        else:
            st.warning("Introduce un token de tenant valido en la barra lateral para sincronizar proyectos.")
            
        st.markdown("#### Exportacion Bidireccional MS Project")
        st.write("Exporta el estado de planificacion actual (WBS) de vuelta a Microsoft Project:")
        xml_export = doc_processor.generate_project_xml(st.session_state.wbs_df)
        st.download_button(
            label="Exportar WBS a MS Project (.xml)",
            data=xml_export,
            file_name="wbs_exportado_civil_twin.xml",
            mime="text/xml"
        )
            
        st.markdown("#### Inicializar Repositorio Git Local")
        st.write("Genera y actualiza archivos de infraestructura (workflows de CI/CD de GitHub Actions, README.md, requirements.txt):")
        
        if st.button("Generar e Inicializar Repositorio"):
            res = github_util.init_local_repo()
            if res:
                st.success("Infraestructura de desarrollo inicializada y confirmada en Git.")
                st.info("Archivos creados: README.md, .github/workflows/test.yml y requirements.txt")
            else:
                st.error("Error al inicializar Git.")
                
        instructions = github_util.prepare_saas_deployment()
        st.markdown("##### Instrucciones para empujar a GitHub corporativo")
        st.code(instructions["github_instructions"], language="bash")
        
    with col_saas_link:
        st.markdown("#### Acceso SaaS para el Gerente (Demo Cloud)")
        st.write(
            "Para que el gerente pruebe de manera remota e interactiva el Gemelo Digital MVP sin necesidad "
            "de instalaciones complejas, CIVIL-TWIN esta preparado para desplegarse mediante un solo enlace:"
        )
        
        st.markdown(
            f"""
            <div style='background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); padding: 25px; border-radius: 12px; margin-top: 15px;'>
                <h4 style='color: #60A5FA; margin-top:0;'>Enlace Demo SaaS Generado</h4>
                <p style='font-size: 0.9rem;'>Haz clic para simular la demo interactiva en la nube o configurar el despliegue automatico:</p>
                <a href='{instructions["streamlit_cloud_link"]}' target='_blank' style='display: inline-block; background: #2563EB; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-right:10px;'>Streamlit Cloud Demo</a>
                <a href='{instructions["huggingface_spaces_link"]}' target='_blank' style='display: inline-block; background: #4B5563; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold;'>Hugging Face Spaces</a>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning(f"Seguridad: {instructions['enterprise_safety']}")
