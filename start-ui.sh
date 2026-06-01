#!/bin/bash
export PORT=${PORT:-10000}
streamlit run app_streamlit.py --server.port $PORT --server.address 0.0.0.0
