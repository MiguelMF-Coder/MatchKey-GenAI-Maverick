from ollama import Client
import pandas as pd
import json
import time

# ---------------  PROMPT --------------- #
PROMPT = """
Extrae la información de la empresa a partir del siguiente texto de su página web:

Texto:
{texto}

Devuelve un JSON con esta estructura EXACTA:

{{
  "values": ["valor1", "valor2", "valor3"],
  "culture_summary": "Resumen de la cultura de la empresa",
}}

REGLAS IMPORTANTES:
1. Todos los campos deben estar presentes: si no hay información explícita, **infierelo razonablemente** a partir del contexto de la empresa.
2. Devuelve solo JSON válido, sin explicaciones ni texto adicional.
3. Mantén los valores concisos, claros y no redundantes.
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
            "values": [],
            "culture_summary": "",
        }


# ---------------  PROGRAMA --------------- #
df = pd.read_csv("backend/app/services/scraping/companies/data/companies_pre_llm.csv")
df = df.drop_duplicates(subset="url_about_us")

# Lista donde meteremos los diccionarios devueltos por el LLM
results = []

# ---------------  ITERAR SOBRE LAS DESCRIPCIONES --------------- #
for i, desc in enumerate(df["clean_text"]):
    print(f"Procesando empresa {i+1}/{len(df)}...")

    data = extract_info_cloud(desc)

    results.append(data)

    time.sleep(0.2)  # para evitar saturar CPU

# Convertir lista de dicts a DF
df_llm = pd.DataFrame(results)

# Unir con el DF original
df_final = df.merge(df_llm, left_index=True, right_index=True)

# ---------------  GUARDAR EN JSON --------------- #
df_final.to_json("backend/app/services/scraping/companies/data/companies_final.json", orient="records", indent=4)

print(" Guardado en backend/app/services/scraping/companies/data/companies_final")