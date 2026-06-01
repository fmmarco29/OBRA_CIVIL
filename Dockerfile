FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias de sistema y herramientas
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de archivos del proyecto
COPY . .

# Asignar permisos de ejecucion al script de inicio
RUN chmod +x start.sh

# Exponer el puerto del frontend (Streamlit) para Hugging Face
EXPOSE 8501

# Endpoint unificado de inicio
ENTRYPOINT ["./start.sh"]
