import requests
import pandas as pd
import time

# --------------- CONFIGURACIÓN API --------------- #
APP_ID = "528c9b37"
APP_KEY = "1a6ce7602df4bc3a6224744a2ec92f49"
RESULTS_PER_PAGE = 50
TOTAL_OFFERS = 350
COUNTRY = "es"
KEYWORDS = ["ia", "machine learning", "data", "data science", "data analytics"]

# ---------------  FUNCION PARA OBTENER LAS OFERTAS --------------- #
def get_offers(keyword, page=1):
    url = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/{page}"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "what": keyword,
        "sort_by": "relevance"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("results", [])


# ---------------  RECOGER TODAS LAS OFERTAS --------------- #
all_jobs = []
offers_needed = TOTAL_OFFERS
page = 1

for keyword in KEYWORDS:
    print(f"Scrapeando ofertas para keyword: {keyword}")
    while offers_needed > 0:
        jobs = get_offers(keyword, page)
        if not jobs:  # Si no hay más resultados
            break
        all_jobs.extend(jobs)
        offers_needed -= len(jobs)
        page += 1
        time.sleep(1)
    page = 1  # Resetear página para la siguiente keyword

# ---------------  ELIMINAR DUPLICADOS --------------- #
seen_urls = set()
unique_jobs = []
for job in all_jobs:
    url = job.get("redirect_url")
    if url not in seen_urls:
        unique_jobs.append(job)
        seen_urls.add(url)

# ---------------  EXTRAER SOLO LA INFO IMPORTANTE --------------- #
jobs_clean = []
for job in unique_jobs:
    jobs_clean.append({
        "title": job.get("title"),
        "company": job.get("company", {}).get("display_name"),
        "location": job.get("location", {}).get("display_name"),
        "area": job.get("location", {}).get("area"),   # lista jerárquica
        "category": job.get("category", {}).get("label"),
        "contract_type": job.get("contract_type"),
        "contract_time": job.get("contract_time"),
        "salary_min": job.get("salary_min"),
        "salary_max": job.get("salary_max"),
        "salary_is_predicted": job.get("salary_is_predicted"),
        "redirect_url": job.get("redirect_url")
    })

# ---------------  GUARDAR EN CSV --------------- #
df = pd.DataFrame(jobs_clean)
df.to_csv("data/jobs_raw.csv", index=False)
print(f"{len(df)} ofertas guardadas en data/jobs_raw.csv")