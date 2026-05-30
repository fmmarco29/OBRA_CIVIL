# CIVIL-TWIN
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
   streamlit run app_streamlit.py
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
