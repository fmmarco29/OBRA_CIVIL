import re
import pandas as pd
import pypdf
import io

class DocumentProcessor:
    """Clase para la ingesta y procesamiento de documentos locales (PDF, Gantt CSV) utilizando técnicas de NLP local"""
    def __init__(self):
        pass

    def extract_metadata_from_text(self, text):
        """
        Extrae variables clave de un texto técnico de obra usando patrones regex y heuristics locales de NLP.
        """
        metadata = {
            "budget": 200000000.0,  # Valor por defecto
            "tunnel_length": 1450.0, # Valor por defecto (m)
            "duration_days": 730,    # Valor por defecto (días)
            "geology": "Basaltos y coladas volcánicas con RMR medio de 60",
            "water_table": "Moderado (flujo estimado < 20 L/min)"
        }
        
        # Limpieza básica
        clean_text = re.sub(r'\s+', ' ', text)
        
        # Regex para Presupuesto / Coste
        # Ej: "200.000.000,00 EUR" o "200 millones de euros"
        budget_match = re.search(r'(?:presupuesto|cost[oe]|licitaci[oó]n).*?(\d+(?:\.\d{3})*(?:,\d{2})?)\s*(?:EUR|euros|€)', clean_text, re.IGNORECASE)
        if budget_match:
            num_str = budget_match.group(1).replace('.', '').replace(',', '.')
            try:
                metadata["budget"] = float(num_str)
            except ValueError:
                pass
        else:
            # Buscar mención de "millones"
            millones_match = re.search(r'(\d+(?:[.,]\d+)?)\s*millones', clean_text, re.IGNORECASE)
            if millones_match:
                try:
                    metadata["budget"] = float(millones_match.group(1).replace(',', '.')) * 1000000.0
                except ValueError:
                    pass

        # Regex para Longitud del Túnel
        # Ej: "túnel... longitud de 1.450 metros" o "1450 m"
        tunnel_match = re.search(r'(?:t[uú]nel|excavaci[oó]n).*?(?:longitud|extensi[oó]n).*?(\d+(?:\.\d{3})*(?:,\d+)?)\s*(?:metros|m\b)', clean_text, re.IGNORECASE)
        if tunnel_match:
            num_str = tunnel_match.group(1).replace('.', '').replace(',', '.')
            try:
                metadata["tunnel_length"] = float(num_str)
            except ValueError:
                pass

        # Regex para Plazo / Duración
        # Ej: "plazo... 730 días" o "duración de 24 meses"
        duration_match = re.search(r'(?:plazo|duraci[oó]n|ejecuci[oó]n).*?(\d+)\s*(?:d[ií]as|meses)', clean_text, re.IGNORECASE)
        if duration_match:
            try:
                val = int(duration_match.group(1))
                unit = duration_match.group(0).lower()
                if "mes" in unit:
                    metadata["duration_days"] = val * 30
                else:
                    metadata["duration_days"] = val
            except ValueError:
                pass

        # Búsqueda de palabras clave para Geología (basaltos, traquitas, RMR, etc.)
        geology_match = re.search(r'(?:geolog[ií]a|roca|terreno|frente).*?([A-Z][^.?!]*?(?:basalto|caliza|arcilla|rmr|suelo|piroclasto)[^.?!]*)', clean_text, re.IGNORECASE)
        if geology_match:
            metadata["geology"] = geology_match.group(1).strip()

        # Búsqueda de nivel freático / agua
        water_match = re.search(r'(?:fre[aá]tico|agua|filtraci|infiltraci|flujo).*?([A-Z][^.?!]*?(?:l/min|fre[aá]tico|agua|filtraci)[^.?!]*)', clean_text, re.IGNORECASE)
        if water_match:
            metadata["water_table"] = water_match.group(1).strip()

        return metadata

    def parse_pdf(self, file_content):
        """
        Extrae texto de un flujo de bytes PDF y obtiene las variables clave del proyecto.
        """
        try:
            pdf_file = io.BytesIO(file_content)
            reader = pypdf.PdfReader(pdf_file)
            full_text = ""
            for page in reader.pages[:10]: # Analizar las primeras 10 páginas para eficiencia
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            return self.extract_metadata_from_text(full_text)
        except Exception as e:
            # En caso de error, devolver valores por defecto
            return self.extract_metadata_from_text("")

    def get_default_wbs(self):
        """
        Genera la estructura de desglose de trabajo (WBS) y el diagrama de Gantt base
        para la carretera con túnel de Fuerteventura (€200M, 730 días).
        """
        data = {
            "Task_ID": [1, 2, 3, 4, 5, 6, 7],
            "Task": [
                "Movilización, Desvíos e Instalación de Faena",
                "Movimiento de Tierras y Desbroce en Carretera",
                "Estructuras y Obras de Drenaje Transversal",
                "Excavación y Sostenimiento de Túnel (1.45m)",
                "Impermeabilización y Revestimiento Estructural de Túnel",
                "Pavimentación, Instalaciones de Seguridad y Ventilación",
                "Señalización, Balizamiento y Pruebas de Recepción"
            ],
            "Start_Day": [1, 31, 121, 151, 451, 601, 671],
            "Duration": [30, 120, 180, 300, 150, 120, 60],
            "Cost": [
                4000000.0,   # €4M
                20000000.0,  # €20M
                30000000.0,  # €30M
                80000000.0,  # €80M
                30000000.0,  # €30M
                20000000.0,  # €20M
                16000000.0   # €16M
            ],
            "Predecessors": ["", "1", "2", "2", "4", "3,5", "6"]
        }
        df = pd.DataFrame(data)
        return df

    def parse_gantt_csv(self, file_content):
        """
        Parsea un archivo CSV subido por el usuario que contenga la planificación Gantt/WBS.
        """
        try:
            # Decodificar el contenido
            csv_file = io.StringIO(file_content.decode('utf-8'))
            df = pd.read_csv(csv_file)
            
            # Normalizar columnas
            required_cols = ["Task_ID", "Task", "Start_Day", "Duration", "Cost", "Predecessors"]
            for col in required_cols:
                if col not in df.columns:
                    # Si falta alguna columna, levantar excepción para usar el default
                    raise ValueError(f"Falta columna requerida en el CSV: {col}")
            
            # Asegurar tipos
            df["Task_ID"] = df["Task_ID"].astype(int)
            df["Start_Day"] = df["Start_Day"].astype(int)
            df["Duration"] = df["Duration"].astype(int)
            df["Cost"] = df["Cost"].astype(float)
            df["Predecessors"] = df["Predecessors"].fillna("").astype(str)
            return df
        except Exception as e:
            # Si hay error, retorna el Gantt por defecto
            return self.get_default_wbs()
