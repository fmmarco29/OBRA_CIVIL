# Ultra-slim build
FROM python:3.11-slim

# Evitar escritura de bytecode y logs para ahorrar disco
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar latex estrictamente minimo (Ahorra > 2GB)
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .
