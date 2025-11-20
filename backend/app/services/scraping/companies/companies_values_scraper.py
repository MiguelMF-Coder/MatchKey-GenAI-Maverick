"""
Scraper de empresas para MatchKey
---------------------------------
Lee backend/app/services/scraping/companies/data/companies_and_links.csv
(con columnas: company, url_about_us) y genera un JSON estructurado con:

[
  {
    "company": "...",
    "url": "...",
    "language": "es" | "en" | "unknown",
    "mission": "...",
    "vision": "...",
    "values": ["...", "..."],
    "culture_summary": "...",
    "raw_text": "...",
    "last_scraped": "2025-11-20T12:34:56Z"
  },
  ...
]

El resultado se guarda en:
  backend/app/services/scraping/values_dataset.json
"""

import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

INPUT_CSV = DATA_DIR / "companies_and_links.csv"
OUTPUT_JSON = BASE_DIR.parent / "values_dataset.json"  # ../values_dataset.json

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0 Safari/537.36"
    )
}

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

WHITESPACE_RE = re.compile(r"\s+")
ES_KEYWORDS = {
    "mission": ["mision", "misión", "nuestro proposito", "nuestro propósito"],
    "vision": ["vision", "visión"],
    "values": ["valores", "nuestros valores"],
    "culture": ["cultura", "cultura corporativa"],
}
EN_KEYWORDS = {
    "mission": ["mission", "our mission", "purpose"],
    "vision": ["vision", "our vision"],
    "values": ["values", "our values", "core values"],
    "culture": ["culture", "company culture", "team culture"],
}


def clean_text(text: str) -> str:
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip()


def detect_language(text: str) -> str:
    text_lower = text.lower()
    es_hits = sum(
        kw in text_lower
        for kw in [
            "misión",
            "mision",
            "visión",
            "valores",
            "quiénes somos",
            "quienes somos",
            "sobre nosotros",
        ]
    )
    en_hits = sum(
        kw in text_lower
        for kw in [
            "mission",
            "vision",
            "values",
            "about us",
            "who we are",
            "our story",
        ]
    )
    if es_hits > en_hits and es_hits > 0:
        return "es"
    if en_hits > es_hits and en_hits > 0:
        return "en"
    return "unknown"


def split_paragraphs(text: str) -> List[str]:
    raw_parts = re.split(r"[.\n]", text)
    parts = [clean_text(p) for p in raw_parts if clean_text(p)]
    return parts


def find_paragraphs_by_keywords(
    paragraphs: List[str],
    keywords: List[str],
    max_paragraphs: int = 3,
) -> List[str]:
    found = []
    for p in paragraphs:
        p_lower = p.lower()
        if any(kw in p_lower for kw in keywords):
            found.append(p)
        if len(found) >= max_paragraphs:
            break
    return found


def extract_sections(text: str) -> Dict[str, Optional[str]]:
    language = detect_language(text)
    paragraphs = split_paragraphs(text)

    if language == "es":
        kw = ES_KEYWORDS
    elif language == "en":
        kw = EN_KEYWORDS
    else:
        kw = {
            "mission": ES_KEYWORDS["mission"] + EN_KEYWORDS["mission"],
            "vision": ES_KEYWORDS["vision"] + EN_KEYWORDS["vision"],
            "values": ES_KEYWORDS["values"] + EN_KEYWORDS["values"],
            "culture": ES_KEYWORDS["culture"] + EN_KEYWORDS["culture"],
        }

    mission_paras = find_paragraphs_by_keywords(paragraphs, kw["mission"], 2)
    vision_paras = find_paragraphs_by_keywords(paragraphs, kw["vision"], 2)
    values_paras = find_paragraphs_by_keywords(paragraphs, kw["values"], 3)
    culture_paras = find_paragraphs_by_keywords(paragraphs, kw["culture"], 3)

    mission = " ".join(mission_paras) if mission_paras else None
    vision = " ".join(vision_paras) if vision_paras else None

    values_list: Optional[List[str]] = None
    if values_paras:
        joined = " ".join(values_paras)
        raw_values = re.split(r"[,:;·•\-]\s*", joined)
        cleaned_values = [clean_text(v) for v in raw_values if len(clean_text(v)) > 2]
        if cleaned_values:
            values_list = cleaned_values

    culture_summary = " ".join(culture_paras) if culture_paras else None

    return {
        "mission": mission,
        "vision": vision,
        "values": values_list,
        "culture_summary": culture_summary,
        "language": language,
    }


def fetch_about_us(url: str, timeout: int = 20) -> Optional[str]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        if resp.status_code >= 400:
            logging.warning(f"[{resp.status_code}] Error al acceder a {url}")
            return None
        return resp.text
    except Exception as e:
        logging.warning(f"Error de red en {url}: {e}")
        return None


def parse_html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    main = soup.find("main") or soup.find("article")
    root = main if main else soup.body or soup

    text = root.get_text(separator=" ")
    return clean_text(text)


def scrape_company(company: str, url: str) -> Optional[Dict]:
    logging.info(f"Scrapeando {company} → {url}")
    html = fetch_about_us(url)
    if not html:
        return None

    raw_text = parse_html_to_text(html)
    if not raw_text or len(raw_text) < 50:
        logging.warning(f"Texto demasiado corto para {company} ({url})")
        return None

    sections = extract_sections(raw_text)
    now_iso = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    return {
        "company": company,
        "url": url,
        "language": sections["language"],
        "mission": sections["mission"],
        "vision": sections["vision"],
        "values": sections["values"],
        "culture_summary": sections["culture_summary"],
        "raw_text": raw_text,
        "last_scraped": now_iso,
    }


def load_companies_and_urls(csv_path: Path) -> List[Dict[str, str]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"No existe el CSV de entrada: {csv_path}")

    df = pd.read_csv(csv_path)

    cols = {c.lower(): c for c in df.columns}
    company_col = cols.get("company")
    url_col = cols.get("url_about_us") or cols.get("url")

    if not company_col or not url_col:
        raise ValueError(
            f"El CSV debe tener columnas 'company' y 'url_about_us' (o 'url'). "
            f"Columnas encontradas: {list(df.columns)}"
        )

    df = df[[company_col, url_col]].rename(
        columns={company_col: "company", url_col: "url"}
    )

    df = df.dropna(subset=["url"])
    df = df.drop_duplicates(subset=["company", "url"])

    records = df.to_dict(orient="records")
    logging.info(f"Cargadas {len(records)} filas (company, url) desde {csv_path}")
    return records


def scrape_all_companies(
    input_csv: Path = INPUT_CSV,
    output_json: Path = OUTPUT_JSON,
    delay_seconds: float = 1.0,
) -> None:
    logging.info("Iniciando scraping de empresas...")
    companies = load_companies_and_urls(input_csv)

    results: List[Dict] = []

    for i, row in enumerate(companies, start=1):
        company = row["company"]
        url = row["url"]
        logging.info(f"[{i}/{len(companies)}] {company}")

        data = scrape_company(company, url)
        if data:
            results.append(data)
        else:
            logging.warning(f"No se pudo obtener datos estructurados para {company}")

        time.sleep(delay_seconds)

    logging.info(f"Scraping terminado. Empresas con datos: {len(results)}")

    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logging.info(f"Dataset guardado en: {output_json}")


if __name__ == "__main__":
    try:
        scrape_all_companies()
    except Exception as e:
        logging.error(f"Error en el scraping: {e}")
        raise
