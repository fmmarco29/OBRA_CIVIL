---
title: Civil Twin Enterprise
sdk: docker
app_port: 8501
emoji: 🏗
colorFrom: blue
colorTo: green
pinned: false
---

# CIVIL-TWIN
> **Gemelo Digital y Control de Costes para Grandes Obras de Infraestructura**  
*Caso de Estudio: Carretera Puerto del Rosario - Caldereta (Túnel Singulado de Fuerteventura, Presupuesto €200,000,000)*

CIVIL-TWIN es una solución corporativa de inteligencia artificial diseñada para operar **completamente en local (On-Premise)** o en la nube mediante contenedores. Garantiza la seguridad y soberanía absoluta de los datos de planificación y geología, eliminando la dependencia de APIs de terceros y protegiendo el secreto industrial.

---

## 🚀 Características del MVP
1. **Ingestión Documental Inteligente (NLP Local)**: Extracción automática de metadatos (BAC, plazos, longitud de túnel, RMR geológico) a partir de pliegos y cronogramas en formato PDF, Gantt CSV o XML de Microsoft Project.
2. **Motor Predictivo de Riesgos Geotécnicos (Machine Learning)**: Clasificador Random Forest entrenado en local basándose en bases de datos públicas de tunelación y carreteras (SCTDataset, OSHA). Predice el nivel de riesgo en el frente de excavación.
3. **Simulador de Monte Carlo de Alto Rendimiento**: Simulación vectorizada ultrarrápida mediante NumPy para pronosticar desviaciones de costes y plazos finales con percentiles P10, P50 y P90.
4. **Gemelo Digital de Costes y Control EVM**: Módulo de Earned Value Management (PV, EV, AC, CPI, SPI, EAC, VAC) para monitorear desviaciones diarias y emitir alertas tempranas críticas.
5. **Generador de Informes LaTeX Corporativos**: Creación instantánea de informes de seguimiento técnico y financiero con diseño ejecutivo listo para compilar e imprimir.
6. **Exportación e Importación Bidireccional con Microsoft Project**: Parser XML nativo integrado para leer y escribir cronogramas compatibles con MS Project sin conversiones intermedias.

---

## 🛠️ Stack Tecnológico
* **Backend & Lógica**: Python 3.12 (FastAPI, Pandas, NumPy, Scikit-learn, PyPDF, NetworkX, pgmpy)
* **Frontend Interactivo**: Streamlit (Plotly interactivo, componentes Dark Mode)
* **CI/CD & Orquestación**: Docker, Docker Compose, GitHub Actions

---

## 📦 Ejecución y Pruebas Locales (Nativo)

Para garantizar la máxima velocidad de procesamiento en local y realizar pruebas rápidas de optimización:

1. Instalar dependencias nativas:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecutar la consola interactiva de Streamlit:
   ```bash
   streamlit run app_streamlit.py
   ```
   La aplicación estará disponible inmediatamente en `http://localhost:8501`.

---

## ☁️ Despliegue en Entorno SaaS (Demo Corporativa)
Para compartir el MVP con el Gerente de Proyecto de manera accesible mediante un enlace seguro y rápido:

1. **Hugging Face Spaces (Recomendado)**:
   - Crear un espacio de tipo **Docker** en Hugging Face.
   - Conectar o subir este repositorio.
   - El frontmatter configurado en este `README.md` orquestará automáticamente el levantamiento conjunto de la API (FastAPI) y el Frontend (Streamlit) en un solo contenedor Fargate gratuito.
2. **Docker Compose**:
   - Levantar la infraestructura multi-contenedor de manera desacoplada:
     ```bash
     docker-compose up --build
     ```
