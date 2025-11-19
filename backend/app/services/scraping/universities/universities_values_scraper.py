from ollama import Client
import pandas as pd
import json
import time

# ---------------  PROMPT --------------- #
PROMPT = """
Extrae la información de la universidad a partir del siguiente texto de su página web:

Texto:
{texto}

Devuelve un JSON con esta estructura EXACTA:

{{
  "university_name": "Nombre de la universidad",
  "values": ["valor1", "valor2", "valor3"],
  "mission": "Breve texto de la misión",
  "vision": "Breve texto de la visión",
  "culture_summary": "Resumen de la cultura de la universidad"
}}

REGLAS IMPORTANTES:
1. Si un campo no está explícitamente en el texto, **infierelo razonablemente** a partir de lo que se entiende sobre la universidad. 
2. Todos los campos deben estar presentes: usa lista vacía [] o string breve como último recurso, pero intenta generar valores relevantes.
3. Devuelve solo JSON válido, sin explicaciones, texto adicional ni notas.
4. No inventes nombres de universidades; "university_name" debe coincidir con el nombre real si está disponible.
5. Mantén los valores concisos y claros, sin redundancia.
"""


# ---------------  CONFIGURACIÓN --------------- #
MODEL = "gpt-oss:120b-cloud"
API_KEY = "95d420411abf4d779651adc5b09480b6.ZRboNs9BwdTvj_1mMmoXdNhQ"

client = Client(
    host="https://ollama.com",
    headers={'Authorization': 'Bearer ' + API_KEY}
)


def extract_info_cloud(texto: str) -> dict:
    mensaje = PROMPT.format(texto=texto)
    try:
        response = client.chat(
            model=MODEL,
            messages=[{'role': 'user', 'content': mensaje}],
            stream=False
        )
        content = response['message']['content']
        return json.loads(content)
    except Exception as e:
        print("ERROR LLM:", e)
        print("CONTENT RECIBIDO:", content if 'content' in locals() else None)
    return {
            "university_name": "",
            "values": [],
            "mission": "",
            "vision": "",
            "culture_summary": "",
            "additional_notes": ""
        }


# ---------------  PROGRAMA --------------- #
df = pd.read_csv("backend/app/services/scraping/universities/data/universidades_pre_llm.csv")

# Lista donde meteremos los diccionarios devueltos por el LLM
results = []

# ---------------  ITERAR SOBRE LAS DESCRIPCIONES --------------- #
for i, desc in enumerate(df["clean_text"]):
    print(f"Procesando universidad {i+1}/{len(df)}...")

    data = extract_info_cloud(desc)

    results.append(data)

    time.sleep(0.2)  # para evitar saturar CPU

# Convertir lista de dicts a DF
df_llm = pd.DataFrame(results)

# Unir con el DF original
df_final = df.merge(df_llm, left_index=True, right_index=True)

# ---------------  GUARDAR EN JSON --------------- #
df_final.to_json("backend/app/services/scraping/universities/data/universities_final.json", orient="records", indent=4)

print(" Guardado en backend/app/services/scraping/universities/data/universities_final")