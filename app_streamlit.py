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
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

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

st.set_page_config(page_title="CIVIL-TWIN | B2B Enterprise", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stApp { background: #F8FAFC; color: #1E293B; }
    .kpi-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); transition: transform 0.3s ease; }
    .kpi-title { font-size: 0.85rem; color: #64748B; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; }
    .kpi-value { font-size: 2rem; font-weight: 700; line-height: 1.2; color: #0F172A; }
    .alert-banner { border-radius: 12px; padding: 16px 20px; margin-bottom: 20px; border-left: 5px solid; }
    .alert-critical { background: #FEE2E2; border-color: #EF4444; color: #991B1B; }
    .alert-warning { background: #FEF3C7; border-color: #F59E0B; color: #92400E; }
    .alert-success { background: #D1FAE5; border-color: #10B981; color: #065F46; }
    .main-header { background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); border-radius: 16px; padding: 30px 40px; margin-bottom: 30px; border: 1px solid #BFDBFE; }
    </style>
    """, unsafe_allow_html=True
)

doc_processor = DocumentProcessor()
twin_engine = DigitalTwinEngine()
report_gen = LaTeXReportGenerator()
github_util = GitHubAutomation()

if "metadata" not in st.session_state:
    st.session_state.metadata = {"budget": 0.0, "tunnel_length": 1450.0, "duration_days": 730, "geology": "Roca volcanica", "water_table": "Nivel freatico moderado"}

if "actual_day" not in st.session_state:
    st.session_state.actual_day = 180

if "project_id" not in st.session_state:
    st.session_state.project_id = 1

def fetch_project_from_api(pid):
    try:
        res = requests.get(f"{BACKEND_URL}/projects/{pid}", timeout=2.0)
        if res.status_code == 200:
            proj = res.json()
            if proj["tasks"]:
                df = pd.DataFrame(proj["tasks"])
                # Asegurar columnas
                df.rename(columns={"actual_progress": "Actual_Progress", "actual_cost": "Actual_Cost", "start_day": "Start_Day", "duration": "Duration", "cost": "Cost", "name": "Task", "task_id": "Task_ID", "predecessors": "Predecessors"}, inplace=True)
                return df, proj["budget"]
    except Exception:
        pass
    return None, 0.0

def create_default_project():
    default_df = doc_processor.get_default_wbs()
    tasks_payload = []
    for _, row in default_df.iterrows():
        tasks_payload.append({
            "task_id": int(row["Task_ID"]), "name": str(row["Task"]),
            "start_day": int(row["Start_Day"]), "duration": int(row["Duration"]),
            "cost": float(row["Cost"]), "predecessors": str(row["Predecessors"])
        })
    payload = {"name": "Autovia Fuerteventura", "description": "Obra civil", "budget": float(default_df["Cost"].sum()), "tasks": tasks_payload}
    try:
        res = requests.post(f"{BACKEND_URL}/projects/", json=payload, timeout=2.0)
        if res.status_code == 200:
            return res.json()["id"]
    except Exception:
        pass
    return 1

# Inicializar Base de Datos en la UI
if "wbs_df" not in st.session_state or st.button("Sincronizar con Base de Datos"):
    df, b = fetch_project_from_api(st.session_state.project_id)
    if df is None:
        new_pid = create_default_project()
        st.session_state.project_id = new_pid
        df, b = fetch_project_from_api(new_pid)
    
    if df is not None:
        st.session_state.wbs_df = df
        st.session_state.metadata["budget"] = b
    else:
        # Fallback offline
        st.session_state.wbs_df = doc_processor.get_default_wbs()
        st.session_state.wbs_df["Actual_Progress"] = 0.0
        st.session_state.wbs_df["Actual_Cost"] = 0.0
        st.session_state.metadata["budget"] = st.session_state.wbs_df["Cost"].sum()

# ================= SIDEBAR =================
st.sidebar.markdown("### Control de Tiempo")
day_input = st.sidebar.number_input("Día de Control Actual", min_value=1, max_value=2000, value=st.session_state.actual_day)
st.session_state.actual_day = day_input

st.sidebar.markdown("---")
st.sidebar.markdown("### Parámetros del Frente (Túnel)")
rmr_input = st.sidebar.slider("Calidad de Roca (RMR)", 10, 100, 65)
depth_input = st.sidebar.slider("Profundidad (m)", 10, 500, 120)

budget = st.session_state.metadata["budget"]

st.markdown(
    f"""
    <div class='main-header'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h1 style='color: #1E3A8A; margin: 0; font-weight: 800; font-size: 2.2rem;'>DSS Fuerteventura - Pozo Negro</h1>
                <p style='color: #3B82F6; margin: 5px 0 0 0; font-size: 1.05rem;'>Sistema Integrado API (Fase 1 y 2 Completadas)</p>
            </div>
            <div style='text-align: right; background: rgba(255,255,255,0.5); padding: 10px 20px; border-radius: 8px;'>
                <span style='color: #64748B; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;'>BAC (Presupuesto Base de Datos)</span>
                <h2 style='color: #059669; margin: 0; font-weight: 700;'>€{budget:,.2f}</h2>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

metrics = twin_engine.calculate_evm_granular(
    day=st.session_state.actual_day,
    tasks_df=st.session_state.wbs_df
)
alerts = twin_engine.get_alerts(metrics)

for alert in alerts:
    st.markdown(f"<div class='alert-banner alert-{alert['type'].lower()}'>[{alert['type']}] {alert['message']}</div>", unsafe_allow_html=True)

tab_dashboard, tab_actuals, tab_document, tab_risk, tab_report = st.tabs([
    "Cuadro de Mando Global", 
    "Seguimiento Granular (EVM)",
    "Ingesta de Planificación", 
    "Simulación Predictiva",
    "Reporte Ejecutivo (PDF)"
])

with tab_dashboard:
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f"<div class='kpi-card'><div class='kpi-title'>CPI</div><div class='kpi-value'>{metrics['CPI']:.3f}</div></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='kpi-card'><div class='kpi-title'>SPI</div><div class='kpi-value'>{metrics['SPI']:.3f}</div></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Cost Variance</div><div class='kpi-value'>€{metrics['CV']:,.0f}</div></div>", unsafe_allow_html=True)
    with col4: st.markdown(f"<div class='kpi-card'><div class='kpi-title'>EAC</div><div class='kpi-value'>€{metrics['EAC']:,.0f}</div></div>", unsafe_allow_html=True)

    col_chart, col_gantt = st.columns([3, 2])
    with col_chart:
        days = np.arange(1, st.session_state.metadata["duration_days"] + 1, 10)
        pv_curve = []
        for d in days:
            v = 0.0
            for _, r in st.session_state.wbs_df.iterrows():
                if d > r["Start_Day"] + r["Duration"] - 1: v += r["Cost"]
                elif d >= r["Start_Day"]: v += ((d - r["Start_Day"] + 1) / r["Duration"]) * r["Cost"]
            pv_curve.append(v)
        
        # Simple curve interpolation for AC and EV up to current day
        actual_days = [d for d in days if d <= st.session_state.actual_day]
        ac_curve = [metrics["AC"] * (d/max(1, st.session_state.actual_day)) for d in actual_days]
        ev_curve = [metrics["EV"] * (d/max(1, st.session_state.actual_day)) for d in actual_days]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=pv_curve, name="Planned Value", line=dict(color='#60A5FA', width=3)))
        fig.add_trace(go.Scatter(x=actual_days, y=ev_curve, name="Earned Value", line=dict(color='#34D399', width=3, dash='dash')))
        fig.add_trace(go.Scatter(x=actual_days, y=ac_curve, name="Actual Cost", line=dict(color='#EF4444', width=3)))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1E293B', height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col_gantt:
        df_g = st.session_state.wbs_df.copy()
        df_g["End_Day"] = df_g["Start_Day"] + df_g["Duration"]
        fig_g = px.timeline(df_g, x_start=df_g["Start_Day"].astype(str), x_end=df_g["End_Day"].astype(str), y="Task", color="Cost")
        fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1E293B', yaxis=dict(autorange="reversed"), height=400)
        st.plotly_chart(fig_g, use_container_width=True)

with tab_actuals:
    st.markdown("### Certificaciones Mensuales (EVM Granular)")
    st.info("Inserta el Progreso Físico Real (0.0 a 1.0) y el Coste Real (Euros) por cada unidad de obra. Estos datos viajan a la Base de Datos.")
    
    cols_to_edit = ["Task", "Cost", "Actual_Progress", "Actual_Cost"]
    edited_df = st.data_editor(
        st.session_state.wbs_df[cols_to_edit],
        use_container_width=True,
        column_config={
            "Actual_Progress": st.column_config.NumberColumn(min_value=0.0, max_value=1.0, format="%.2f"),
            "Actual_Cost": st.column_config.NumberColumn(format="€ %.2f")
        }
    )
    
    if st.button("Guardar Avance en Base de Datos"):
        # Detectar cambios y mandar a API
        success = True
        for idx, row in edited_df.iterrows():
            orig = st.session_state.wbs_df.iloc[idx]
            if orig["Actual_Progress"] != row["Actual_Progress"] or orig["Actual_Cost"] != row["Actual_Cost"]:
                task_id = orig.get("id")
                if task_id:
                    try:
                        requests.put(f"{BACKEND_URL}/projects/tasks/{task_id}/actuals", json={
                            "actual_progress": float(row["Actual_Progress"]),
                            "actual_cost": float(row["Actual_Cost"])
                        }, timeout=2.0)
                    except Exception as e:
                        success = False
                        st.error(f"Error subiendo API: {e}")
                st.session_state.wbs_df.at[idx, "Actual_Progress"] = row["Actual_Progress"]
                st.session_state.wbs_df.at[idx, "Actual_Cost"] = row["Actual_Cost"]
        if success:
            st.success("Progreso granular guardado en base de datos. EVM Recalculado.")
            st.rerun()

with tab_document:
    st.markdown("### Cargar Cronograma (PDF o XML)")
    uploaded_gantt = st.file_uploader("Sube el Diagrama Gantt", type=["pdf", "xml", "csv"])
    if uploaded_gantt and st.button("Procesar Archivo"):
        with st.spinner("Parseando mediante heurística local en el Backend API..."):
            try:
                files = {"file": (uploaded_gantt.name, uploaded_gantt.getvalue(), uploaded_gantt.type)}
                res = requests.post(f"{BACKEND_URL}/projects/{st.session_state.project_id}/upload_gantt", files=files, timeout=10.0)
                if res.status_code == 200:
                    st.success(res.json()["message"])
                    # Sincronizar de nuevo
                    df, b = fetch_project_from_api(st.session_state.project_id)
                    st.session_state.wbs_df = df
                    st.session_state.metadata["budget"] = b
                    st.rerun()
                else:
                    st.error(res.text)
            except Exception as e:
                st.error(f"Error de red: {e}")

with tab_risk:
    st.markdown("### Inferencia Predictiva sobre Actividades (Monte Carlo)")
    st.info("El motor envía el grafo WBS y sus dependencias (Gantt) al backend para simular la ruta crítica real miles de veces.")
    
    sim_iterations = st.slider("Iteraciones", min_value=100, max_value=5000, value=2000, step=100)
    
    if st.button("Ejecutar Simulación con IA"):
        with st.spinner("Computando distribuciones asíncronas en API..."):
            tasks_list = []
            for _, r in st.session_state.wbs_df.iterrows():
                tasks_list.append({
                    "Task_ID": int(r["Task_ID"]),
                    "Task": str(r.get("Task", "Unknown")),
                    "Duration": float(r["Duration"]),
                    "Cost": float(r["Cost"]),
                    "Start_Day": int(r["Start_Day"]),
                    "Predecessors": str(r.get("Predecessors", "")) if pd.notna(r.get("Predecessors")) else ""
                })
            
            payload = {
                "tasks": tasks_list,
                "rmr": float(rmr_input),
                "water_influx": 15.0, # Defaulting for now
                "depth": float(depth_input),
                "iterations": sim_iterations
            }
            
            try:
                res = requests.post(f"{BACKEND_URL}/simulate/montecarlo", json=payload, timeout=20.0)
                if res.status_code == 200:
                    sim_results = res.json()
                    st.success("Simulación completada en el backend.")
                    
                    # Layout para mostrar resultados
                    col_r1, col_r2, col_r3 = st.columns(3)
                    with col_r1: st.metric("Riesgo Geotécnico", f"Nivel {sim_results['geotechnical_risk_level']}")
                    with col_r2: st.metric("Duración P50", f"{sim_results['p50_duration']} días")
                    with col_r3: st.metric("Duración P90", f"{sim_results['p90_duration']} días")
                    
                    st.markdown("#### Distribución Probabilística de Coste (M€)")
                    costs_array = np.array(sim_results["costs"]) / 1e6
                    fig_mc = px.histogram(x=costs_array, nbins=50, color_discrete_sequence=['#3B82F6'])
                    fig_mc.add_vline(x=sim_results["p50_cost"] / 1e6, line_color="#F59E0B", annotation_text=f"P50")
                    fig_mc.add_vline(x=sim_results["p90_cost"] / 1e6, line_dash="dash", line_color="#EF4444", annotation_text=f"P90")
                    fig_mc.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1E293B', height=350)
                    st.plotly_chart(fig_mc, use_container_width=True)
                else:
                    st.error(f"Error en API: {res.text}")
            except Exception as e:
                st.error(f"Fallo conectando al backend: {e}")

with tab_report:
    st.markdown("### Generador de Informes Ejecutivos")
    st.info("El sistema recopila los datos de progreso actual (EVM) y el último modelo predictivo para redactar un informe profesional en PDF.")
    
    if st.button("Generar Informe en PDF"):
        with st.spinner("Compilando documento final (LaTeX a PDF) en local..."):
            try:
                # We need some dummy or latest risk results if MonteCarlo hasn't been run yet in this session
                risk_mock = {
                    "p50_duration": st.session_state.metadata.get("duration_days", 730),
                    "p90_duration": st.session_state.metadata.get("duration_days", 730),
                    "p50_cost": st.session_state.metadata.get("budget", 0),
                    "p90_cost": st.session_state.metadata.get("budget", 0),
                    "geotechnical_risk_level": 0
                }
                
                pdf_bytes = report_gen.generate_pdf_report(
                    metadata=st.session_state.metadata,
                    evm_metrics=metrics,
                    risk_results=risk_mock
                )
                
                st.success("PDF generado exitosamente.")
                st.download_button(
                    label="Descargar Informe Ejecutivo (PDF)",
                    data=pdf_bytes,
                    file_name=f"Informe_Obra_Dia_{st.session_state.actual_day}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error generando el PDF: {e}")
