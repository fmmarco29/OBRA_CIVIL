import os
import subprocess

class GitHubAutomation:
    """Clase para automatizar la inicialización del repositorio local y la preparación de archivos para el despliegue SaaS"""
    def __init__(self, repo_path="/home/fernando/OBRA_FUERTEVENTURA"):
        self.repo_path = repo_path

    def init_local_repo(self):
        """
        Inicializa Git localmente si no existe, genera los archivos de infraestructura
        (README, Dockerfile, Compose, CI/CD) y hace un commit limpio.
        """
        # 1. Crear directorios de infraestructura si no existen
        os.makedirs(os.path.join(self.repo_path, ".github", "workflows"), exist_ok=True)
        
        # 2. Generar README.md
        readme_path = os.path.join(self.repo_path, "README.md")
        readme_content = """# CIVIL-TWIN
> **Gemelo Digital y Control de Costes para Grandes Obras de Infraestructura**  
*Caso de Estudio: Carretera Puerto del Rosario - Caldereta (Túnel Singulado de Fuerteventura, Presupuesto €200,000,000)*

CIVIL-TWIN es una solución corporativa de inteligencia artificial diseñada para operar **completamente en local (On-Premise)**. Garantiza la seguridad y soberanía absoluta de los datos de planificación y geología, eliminando la dependencia de APIs de terceros y protegiendo el secreto industrial.

---

## 🚀 Características del MVP
1. **Ingestión Documental Inteligente (NLP Local)**: Extracción automática de metadatos (BAC, plazos, longitud de túnel, RMR geológico) a partir de pliegos y cronogramas en formato PDF o Gantt CSV.
2. **Motor Predictivo de Riesgos Geotécnicos (Machine Learning)**: Clasificador Random Forest entrenado en local basándose en bases de datos públicas de tunelación y carreteras (SCTDataset, OSHA). Predice el nivel de riesgo en el frente de excavación.
3. **Simulador de Monte Carlo de Alto Rendimiento**: Simulación vectorizada ultrarrápida mediante NumPy (hasta 10,000 iteraciones instantáneas) para pronosticar desviaciones de costes y plazos finales con percentiles P10, P50 y P90.
4. **Gemelo Digital de Costes y Control EVM**: Módulo de Earned Value Management (PV, EV, AC, CPI, SPI, EAC, VAC) para monitorear desviaciones diarias y emitir alertas tempranas críticas.
5. **Generador de Informes LaTeX Corporativos**: Creación instantánea de informes de seguimiento técnico y financiero con diseño ejecutivo listo para compilar e imprimir.

---

## 🛠️ Stack Tecnológico
* **Backend & Lógica**: Python 3.12 (Pandas, NumPy, Scikit-learn, PyPDF, Jinja2)
* **Frontend Interactivo**: Streamlit (Plotly interactivo, componentes Dark Mode)
* **CI/CD**: GitHub Actions (Validación automatizada de pruebas)

---

## 📦 Ejecución y Pruebas Locales (Nativo)

Para garantizar la máxima velocidad de procesamiento en local y realizar pruebas rápidas de optimización:

1. Instalar dependencias nativas:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecutar la consola interactiva de Streamlit:
   ```bash
   streamlit run app.py
   ```
   La aplicación estará disponible inmediatamente en `http://localhost:8501`.

*(Nota: La infraestructura cuenta con archivos de Docker y Docker-Compose para despliegues aislados futuros, pero se prioriza la ejecución nativa en esta fase de optimización y pruebas).*

---

## ☁️ Despliegue en Entorno SaaS (Demo Corporativa)
Para compartir el MVP con el Gerente de Proyecto de manera accesible mediante un enlace seguro y rápido:

1. **Hugging Face Spaces (Recomendado)**:
   - Crear un espacio de tipo **Streamlit** en Hugging Face.
   - Subir el repositorio de código.
   - Enlace demo provisto automáticamente por Hugging Face en su infraestructura en la nube.
2. **Streamlit Community Cloud**:
   - Conectar tu cuenta de GitHub.
   - Seleccionar el repositorio `OBRA_CIVIL` y hacer clic en **Deploy**.
"""
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        # 3. Generar Dockerfile
        dockerfile_path = os.path.join(self.repo_path, "Dockerfile")
        dockerfile_content = """FROM python:3.12-slim

# Evitar que Python escriba archivos .pyc y forzar salida sin buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \\
    git \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto por defecto de Streamlit
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""
        with open(dockerfile_path, "w", encoding="utf-8") as f:
            f.write(dockerfile_content)

        # 4. Generar docker-compose.yml
        compose_path = os.path.join(self.repo_path, "docker-compose.yml")
        compose_content = """version: "3.8"

services:
  civil-twin:
    build: .
    container_name: civil_twin_mvp
    ports:
      - "8501:8501"
    restart: always
    volumes:
      - .:/app
    environment:
      - STREAMLIT_THEME_BASE=dark
"""
        with open(compose_path, "w", encoding="utf-8") as f:
            f.write(compose_content)

        # 5. Generar requirements.txt
        req_path = os.path.join(self.repo_path, "requirements.txt")
        req_content = """streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
scikit-learn>=1.2.0
pypdf>=3.9.0
jinja2>=3.1.0
pytest>=7.0.0
"""
        with open(req_path, "w", encoding="utf-8") as f:
            f.write(req_content)

        # 6. Generar GitHub Actions Workflow
        ci_path = os.path.join(self.repo_path, ".github", "workflows", "test.yml")
        ci_content = """name: CIVIL-TWIN CI

on:
  push:
    branches: [ master, main ]
  pull_request:
    branches: [ master, main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run unit tests
      run: |
        python -m pytest tests/ -v
"""
        with open(ci_path, "w", encoding="utf-8") as f:
            f.write(ci_content)

        # Hacer git add y git commit en el repositorio local de forma robusta
        try:
            subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)
            # Comprobar si hay cambios listos para commit
            status_res = subprocess.run(["git", "status", "--porcelain"], cwd=self.repo_path, capture_output=True, text=True)
            if status_res.stdout.strip():
                subprocess.run(["git", "commit", "-m", "feat: optimize Monte Carlo vectorization and focus on native local execution"], cwd=self.repo_path, check=True)
            return True
        except Exception as e:
            return False

    def prepare_saas_deployment(self):
        """
        Retorna enlaces clave e instrucciones detalladas para el gerente de obra sobre el despliegue del MVP.
        """
        return {
            "github_instructions": "Para empujar el código al repositorio corporativo de GitHub:\n"
                                   "1. git remote add origin <URL_DE_TU_REPOSITORIO>\n"
                                   "2. git branch -M main\n"
                                   "3. git push -u origin main",
            "streamlit_cloud_link": "https://share.streamlit.io/",
            "huggingface_spaces_link": "https://huggingface.co/spaces",
            "enterprise_safety": "Nota de Seguridad Corporativa: El MVP corre 100% en local. Para el despliegue SaaS sin comprometer datos confidenciales, la simulación opera con variables parametrizadas sin requerir conexiones a servidores externos."
        }
