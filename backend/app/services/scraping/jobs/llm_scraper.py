from ollama import Client
import pandas as pd
import json
import time

# ---------------  PROMPT --------------- #
PROMPT = """
Eres un asistente experto en análisis de ofertas de empleo.

Tu tarea es LEER la descripción de una oferta y devolver EXACTAMENTE este JSON:

{{
  "experience_required": int | "",
  "education_required": "",
  "skills_must": [],
  "skills_nice": [],
  "seniority": "",
  "job_type": "",
  "tech_stack": [],
  "soft_skills": [],
  "languages": [],
  "benefits": [],
  "category": ""
}}

REGLAS IMPORTANTES:
1. SIEMPRE devuelve JSON válido sin texto alrededor.
2. experience_required → número entero (años) o "".
   - Si dice "mínimo X años", devuelve X.
   - Si dice "sin experiencia" o "0 años", devuelve 0.
3. Las listas NO deben contener duplicados.
4. seniority debe ser una de:
   ["Junior", "Mid", "Senior", "Lead", "Manager", ""]
5. job_type debe ser una de:
   ["Full-time", "Part-time", "Internship", "Freelance", "Contract", ""]
6. category debe elegirse entre:
   ["Data Science", "Machine Learning", "AI", "Software Engineering",
    "Business Intelligence", "Cybersecurity", "Cloud", "Other"]
7. Si NO está claro → usa "" o lista vacía.
8. tech_stack debe contener SOLO tecnologías concretas (Python, SQL, AWS, TensorFlow, etc.).
9. NO inventes información. Reflexiona brevemente antes de responder.
10. Responde SOLO JSON.

Descripción:
{texto}
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
            "experience_required": "",
            "education_required": "",
            "skills_must": [],
            "skills_nice": [],
            "seniority": "",
            "job_type": "",
            "tech_stack": [],
            "soft_skills": [],
            "languages": [],
            "benefits": [],
            "category": ""
        }


# ---------------  PROGRAMA --------------- #
df = pd.read_csv("data/jobs_clean.csv")

# Lista donde meteremos los diccionarios devueltos por el LLM
results = []

# ---------------  ITERAR SOBRE LAS DESCRIPCIONES --------------- #
for i, desc in enumerate(df["description_full"]):
    print(f"Procesando oferta {i+1}/{len(df)}...")

    data = extract_info_cloud(desc)

    results.append(data)

    time.sleep(0.2)  # para evitar saturar CPU

# Convertir lista de dicts a DF
df_llm = pd.DataFrame(results)

# Unir con el DF original
df_final = df.merge(df_llm, suffixes=["_jobs", "_llm"], left_index=True, right_index=True)

# ---------------  GUARDAR EN JSON Y CSV --------------- #
df_final.to_json("data/jobs_final.json", orient="records", indent=4)
df_final.to_csv("data/jobs_final.csv", index=False)

print("\n Extracción completada.")
print(" Guardado en data/jobs_final.json y data/jobs_final.csv")