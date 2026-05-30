import pytest
import pandas as pd
import numpy as np

def test_imports():
    try:
        import src.document_processor as dp
        import src.risk_engine as re
        import src.digital_twin as dt
        import src.report_generator as rg
        import src.github_automation as ga
        assert dp is not None
        assert re is not None
        assert dt is not None
        assert rg is not None
        assert ga is not None
    except ImportError as e:
        assert False, f"Error al importar módulos: {e}"

def test_document_processor_default_gantt():
    from src.document_processor import DocumentProcessor
    dp = DocumentProcessor()
    wbs = dp.get_default_wbs()
    assert isinstance(wbs, pd.DataFrame)
    assert not wbs.empty
    assert "Task" in wbs.columns
    assert "Duration" in wbs.columns
    assert "Cost" in wbs.columns
    total_cost = wbs["Cost"].sum()
    assert np.isclose(total_cost, 200000000.0, rtol=0.05)

def test_document_processor_nlp_extraction():
    from src.document_processor import DocumentProcessor
    dp = DocumentProcessor()
    sample_spec = """
    PROYECTO DE CONSTRUCCIÓN DE LA CARRETERA PUERTO DEL ROSARIO - CALDERETA (FUERTEVENTURA)
    Presupuesto base de licitación: 200.000.000,00 EUR.
    El proyecto contempla la ejecución de un túnel bidireccional con una longitud total de 1.450 metros.
    El plazo total de ejecución estimado para la totalidad de las obras es de 730 días.
    La geología esperada en el frente de excavación se compone principalmente de basaltos macizos (RMR de 65).
    Se estima un nivel freático moderado con posible flujo de agua de 15 L/min.
    """
    metadata = dp.extract_metadata_from_text(sample_spec)
    assert metadata["budget"] == 200000000.0
    assert metadata["tunnel_length"] == 1450.0
    assert metadata["duration_days"] == 730
    assert "basaltos" in metadata["geology"].lower()

def test_geotechnical_risk_model():
    from src.risk_engine import GeotechnicalRiskModel
    model = GeotechnicalRiskModel()
    model.train()
    
    prediction = model.predict([[70.0, 50.0, 5.0]])
    assert prediction[0] in [0, 1, 2]
    
    prediction_high = model.predict([[25.0, 250.0, 80.0]])
    assert prediction_high[0] in [0, 1, 2]
    assert prediction_high[0] >= prediction[0]

def test_monte_carlo_simulator():
    from src.risk_engine import MonteCarloSimulator
    from src.document_processor import DocumentProcessor
    dp = DocumentProcessor()
    wbs = dp.get_default_wbs()
    
    simulator = MonteCarloSimulator()
    results = simulator.run_simulation(wbs, iterations=100)
    
    assert "durations" in results
    assert "costs" in results
    assert "p10_duration" in results
    assert "p50_duration" in results
    assert "p90_duration" in results
    assert "p90_cost" in results
    
    assert len(results["durations"]) == 100
    assert results["p50_duration"] > 0
    assert results["p90_cost"] >= results["p10_cost"]

def test_digital_twin_evm():
    from src.digital_twin import DigitalTwinEngine
    from src.document_processor import DocumentProcessor
    
    dp = DocumentProcessor()
    wbs = dp.get_default_wbs()
    
    engine = DigitalTwinEngine(budget=200000000.0, total_days=730)
    actual_cost = 105000000.0
    actual_progress = 0.48
    
    metrics = engine.calculate_evm(day=365, actual_cost=actual_cost, actual_progress=actual_progress, tasks_df=wbs)
    
    assert metrics["PV"] > 0
    assert metrics["EV"] == 200000000.0 * actual_progress
    assert metrics["AC"] == actual_cost
    assert "CPI" in metrics
    assert "SPI" in metrics
    assert "CV" in metrics
    assert "SV" in metrics
    
    assert np.isclose(metrics["CPI"], 96000000.0 / 105000000.0, rtol=0.01)
    
    alerts = engine.get_alerts(metrics)
    assert isinstance(alerts, list)

def test_latex_report_generator():
    from src.report_generator import LaTeXReportGenerator
    
    generator = LaTeXReportGenerator()
    
    metadata = {
        "budget": 200000000.0,
        "tunnel_length": 1450.0,
        "duration_days": 730,
        "geology": "Basaltos compactos",
        "water_table": "Bajo"
    }
    
    evm_metrics = {
        "Day": 180,
        "PV": 45000000.0,
        "EV": 48000000.0,
        "AC": 50000000.0,
        "CV": -2000000.0,
        "SV": 3000000.0,
        "CPI": 0.96,
        "SPI": 1.07,
        "EAC": 208333333.33,
        "ETC": 158333333.33,
        "VAC": -8333333.33,
        "Budget": 200000000.0,
        "Total_Days": 730
    }
    
    risk_results = {
        "p50_duration": 745,
        "p90_duration": 810,
        "p50_cost": 205000000.0,
        "p90_cost": 224000000.0,
        "geotechnical_risk_level": 1
    }
    
    report = generator.generate_report(metadata, evm_metrics, risk_results)
    
    assert isinstance(report, str)
    assert "\\documentclass" in report
    assert "\\begin{document}" in report
    assert "EVM" in report
    assert "Monte Carlo" in report
    assert "Fuerteventura" in report
    assert "\\end{document}" in report

def test_github_automation():
    from src.github_automation import GitHubAutomation
    import os
    
    ga = GitHubAutomation()
    info = ga.prepare_saas_deployment()
    
    assert "github_instructions" in info
    assert "streamlit_cloud_link" in info
    assert "huggingface_spaces_link" in info
    
    # Probar que inicializa y crea archivos
    res = ga.init_local_repo()
    assert res is True
    
    # Comprobar existencia de archivos clave generados
    assert os.path.exists("/home/fernando/OBRA_FUERTEVENTURA/README.md")
    assert os.path.exists("/home/fernando/OBRA_FUERTEVENTURA/Dockerfile")
    assert os.path.exists("/home/fernando/OBRA_FUERTEVENTURA/docker-compose.yml")
    assert os.path.exists("/home/fernando/OBRA_FUERTEVENTURA/requirements.txt")
    assert os.path.exists("/home/fernando/OBRA_FUERTEVENTURA/.github/workflows/test.yml")
