# CIVIL-TWIN 🏗️🛤️🚇
> **Gemelo Digital y Control de Costes para Grandes Obras de Infraestructura**  
*Caso de Estudio: Carretera Puerto del Rosario - Caldereta (Túnel Singulado de Fuerteventura, Presupuesto €200,000,000)*

CIVIL-TWIN es una solución corporativa de inteligencia artificial diseñada para operar **completamente en local (On-Premise)**. Garantiza la seguridad y soberanía absoluta de los datos de planificación y geología, eliminando la dependencia de APIs de terceros.

---

## 🚀 Características del MVP
1. **Ingestión Documental Inteligente (NLP Local)**: Extracción automática de metadatos (BAC, plazos, longitud de túnel, RMR geológico) a partir de pliegos y cronogramas en formato PDF o Gantt CSV.
2. **Motor Predictivo de Riesgos Geotécnicos (Machine Learning)**: Clasificador Random Forest entrenado en local basándose en bases de datos públicas de tunelación y carreteras (SCTDataset, OSHA). Predice el nivel de riesgo en el frente de excavación.
3. **Simulador Probabilístico de Monte Carlo**: Simulación con 5,000 iteraciones para pronosticar desviaciones de costes y plazos finales con percentiles P10, P50 y P90.
4. **Gemelo Digital de Costes y Control EVM**: Módulo de Earned Value Management (PV, EV, AC, CPI, SPI, EAC, VAC) para monitorear desviaciones diarias y emitir alertas tempranas críticas.
5. **Generador de Informes LaTeX Corporativos**: Creación instantánea de informes de seguimiento técnico y financiero con diseño ejecutivo listo para compilar e imprimir.

---

## 🛠️ Stack Tecnológico
* **Backend & Lógica**: Python 3.12 (Pandas, NumPy, Scikit-learn, PyPDF, Jinja2)
* **Frontend Interactivo**: Streamlit (Plotly interactivo, componentes Dark Mode)
* **Contenedores**: Docker / Docker-Compose
* **CI/CD**: GitHub Actions (Validación automatizada de pruebas)

---

## 📦 Ejecución y Despliegue Local

### Opción 1: Ejecutar directamente en Python
1. Instalar dependencias:
   ```bash
   pip install streamlit pandas numpy plotly scikit-learn pypdf
   ```
2. Ejecutar la aplicación:
   ```bash
   streamlit run app.py
   ```

### Opción 2: Ejecutar con Docker (Recomendado)
Para levantar la solución en tu propio servidor local de manera aislada:
```bash
docker-compose up --build
```
La aplicación estará disponible en `http://localhost:8501`.

---

## ☁️ Despliegue en Entorno SaaS (Demo Corporativa)
Para compartir el MVP con el Gerente de Proyecto de manera accesible mediante un enlace seguro y rápido:

1. **Hugging Face Spaces (Recomendado)**:
   - Crear un espacio de tipo **Streamlit** en Hugging Face.
   - Subir el repositorio de código.
   - Enlace demo provisto automáticamente por Hugging Face en su infraestructura en la nube.
2. **Streamlit Community Cloud**:
   - Conectar tu cuenta de GitHub.
   - Seleccionar el repositorio `CIVIL-TWIN` y hacer clic en **Deploy**.
