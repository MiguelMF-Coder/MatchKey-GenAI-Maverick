from ollama import Client
import pandas as pd
import json
import time

# ---------------  PROMPT --------------- #
PROMPT = """
Eres un analista empresarial experto. Analiza el siguiente texto procedente de la página web corporativa de una empresa:

Texto:
{texto}

Devuelve SOLO un JSON válido con la siguiente estructura EXACTA:

{{
  "values": ["valor1", "valor2", "valor3"],
  "culture_summary": "Resumen claro y profesional de la cultura de la empresa"
}}

REGLAS IMPORTANTES:
- NO escribas explicaciones fuera del JSON.
- Extrae exactamente 3 valores clave que definan la identidad o filosofía de la empresa.
- Si los valores no aparecen de forma explícita, infiérelos profesionalmente a partir del tono y contenido.
- La cultura debe describirse en 2–3 frases como máximo.
- No repitas información ni incluyas frases genéricas.
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
            "culture_summary": ""
        }


# ---------------  PROGRAMA --------------- #
df = pd.read_csv("backend/app/services/scraping/companies/data/companies_pre_llm.csv")
df = df.dropna().reset_index()
# df = df.drop_duplicates(subset="url_about_us")

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