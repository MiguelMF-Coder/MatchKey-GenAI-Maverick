# backend/app/services/scraping/companies/companies_scrapper.py

import pandas as pd
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

INPUT_TXT = DATA_DIR / "about_us.txt"
OUTPUT_CSV = DATA_DIR / "companies_and_links.csv"

# Mapeo manual dominio → nombre de empresa (puedes ir ampliándolo)
DOMAIN_TO_COMPANY = {
    "global.ntt": "NTT",
    "henneo.com": "Henneo",
    "caixabank.com": "Caixabank",
    "getnet.eu": "Getnet",
    "merlindp.com": "Merlin Digital Partner",
    "getdarwin.ai": "Darwin AI",
    "qualentum.com": "Qualentum",
    "plexus.es": "Plexus",
    "grupodigital.eu": "Grupo Digital",
    "socialyou.es": "Social You",
    "extia-group.com": "Extia",
    "soprasteria.es": "Sopra-Steria",
    "accenture.com": "Accenture",
    "rentokil-initial.com": "Rentokil Initial",
    "krell-consulting.com": "Krell Consulting & Training",
    "seat.es": "SEAT SA",
    "raona.com": "Raona",
    "manpower.es": "Manpower Trabajo Temporal",
    "randstad.es": "Randstad ES",
    "uspceu.com": "Fundación Universitaria San Pablo CEU",
    "babelgroup.com": "Babel",
    "page.com": "Michael Page",
    "zylk.net": "ZYLK",
    "ikerlan.es": "Ikerlan",
    "irium.es": "IRIUM - Spain",
    "plainconcepts.com": "Plain Concepts",
    "bipgroup.com": "BIP Group",
    "monlaucorporate.com": "Monlau Centre d'Estudis, S.A.",
    "tecnalia.com": "Tecnalia",
    "slashmobility.com": "SlashMobility",
    "rdt.com": "RDT",
    "infinityneural.com": "Infinity Neural",
    "primer-impacto.com": "Primer Impacto",
    "sener.es": "Sener",
    "bkhengineering.com": "BKH Engineering",
    "lefebvre.es": "Lefebvre",
    "multiopticas.com": "Multiopticas",
    "ey.com": "EY",
    "t-systems.com": "T-Systems Iberia",
    "talent-r.com": "Talent-R",
    "prishia.es": "Prishia",
    # añade más dominios si los vas viendo
}


def infer_company_from_url(url: str) -> str | None:
    if not url or str(url).lower() == "nan":
        return None

    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    domain = domain.lstrip("www.")

    if not domain:
        return None

    # 1) Si está en el diccionario, usamos ese nombre
    if domain in DOMAIN_TO_COMPANY:
        return DOMAIN_TO_COMPANY[domain]

    # 2) Si no está, usamos la parte antes del primer punto
    base = domain.split(".")[0]
    if not base:
        return None

    # Cambiamos guiones por espacios y capitalizamos
    name = base.replace("-", " ").strip()
    if not name:
        return None
    return name.title()


def main():
    if not INPUT_TXT.exists():
        raise FileNotFoundError(f"No existe {INPUT_TXT}")

    urls: list[str] = []
    with open(INPUT_TXT, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.lower() == "nan":
                continue
            urls.append(line)

    records: list[dict] = []
    for url in urls:
        company = infer_company_from_url(url)
        if not company:
            continue
        records.append({"company": company, "url_about_us": url})

    df = pd.DataFrame(records).drop_duplicates(subset=["company", "url_about_us"])

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Guardado {len(df)} filas en {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
