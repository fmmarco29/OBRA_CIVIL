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
