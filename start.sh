#!/bin/bash
# Iniciar el backend FastAPI en segundo plano
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &

# Esperar un instante para que el backend este activo
sleep 2

# Iniciar el frontend Streamlit en primer plano
streamlit run app_streamlit.py --server.port=8501 --server.address=0.0.0.0
