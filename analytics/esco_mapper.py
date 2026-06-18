"""
analytics/esco_mapper.py — Mapeo MatchKey <-> ESCO (Fase 1 del TFG).

Produce:
    data/esco/matchkey_skills_to_esco.csv
    data/esco/matchkey_categories_to_esco_occupations.csv
    data/esco/_coverage_summary.csv

Método (lo que pide CLAUDE.md: "exact + fuzzy con TF-IDF"):
  1) EXACTO: skill normalizada == preferredLabel o algún altLabel de ESCO (normalizados).
  2) FUZZY:  para lo no resuelto, TF-IDF de n-gramas de caracteres (char_wb 3-5) sobre los
     preferredLabel de ESCO + similitud coseno; se acepta el top-1 si supera un umbral.
  3) NONE:   por debajo del umbral -> sin correspondencia (resultado válido y reportado).

Honestidad (CLAUDE.md): muchas soft skills de MatchKey están en ESPAÑOL y ESCO se cosecha en
INGLÉS, por lo que NO mapearán; eso es un hallazgo, no un fallo. `category_llm` es silver-standard.

Decisiones defendibles y configurables:
  - FUZZY_THRESHOLD: umbral de coseno para aceptar match fuzzy (default 0.60).
  - Se guarda la `similarity` de cada match para poder auditar/justificar el umbral.

Uso (tras ejecutar data/esco/download_esco.py):
    .venv\\Scripts\\python.exe analytics\\esco_mapper.py
"""

from __future__ import annotations

import re
import unicodedata

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils import (
    REPO_ROOT,
    MATCHKEY_DIR,
    ESCO_DIR,
    save_csv,
)

FUZZY_THRESHOLD = 0.70  # coseno mínimo para aceptar match fuzzy (alto = más precisión; evita p.ej. 'power bi'->'use power tools')


# --------------------------------------------------------------------------
# Normalización
# --------------------------------------------------------------------------
def norm(s) -> str:
    """minúsculas + strip acentos + colapsa espacios. Para comparar labels."""
    if s is None:
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(s.split())


# --------------------------------------------------------------------------
# Carga de inventarios
# --------------------------------------------------------------------------
def load_matchkey_skill_inventory() -> pd.DataFrame:
    """Une skills de candidatos y de vacantes en un inventario único con frecuencia y origen."""
    cand = pd.read_csv(MATCHKEY_DIR / "candidate_skills.csv")
    jobs = pd.read_csv(MATCHKEY_DIR / "job_skills.csv")

    cand_skills = cand["skill"].dropna().astype(str)
    job_skills = jobs["skill"].dropna().astype(str)

    rows = {}
    for s in cand_skills:
        k = norm(s)
        if not k:
            continue
        r = rows.setdefault(k, {"matchkey_skill_norm": k, "example_original": s, "freq_candidates": 0, "freq_jobs": 0})
        r["freq_candidates"] += 1
    for s in job_skills:
        k = norm(s)
        if not k:
            continue
        r = rows.setdefault(k, {"matchkey_skill_norm": k, "example_original": s, "freq_candidates": 0, "freq_jobs": 0})
        r["freq_jobs"] += 1

    df = pd.DataFrame(rows.values())
    df["freq_total"] = df["freq_candidates"] + df["freq_jobs"]
    df["source"] = df.apply(
        lambda x: "both" if x.freq_candidates and x.freq_jobs else ("candidate" if x.freq_candidates else "job"),
        axis=1,
    )
    return df.sort_values("freq_total", ascending=False).reset_index(drop=True)


def load_esco(filename: str) -> pd.DataFrame:
    df = pd.read_csv(ESCO_DIR / filename)
    df["preferred_label"] = df["preferred_label"].fillna("")
    df["alt_labels"] = df.get("alt_labels", "").fillna("")
    return df


# --------------------------------------------------------------------------
# Índice exacto (preferred + alt labels)
# --------------------------------------------------------------------------
def build_exact_index(esco: pd.DataFrame) -> dict[str, dict]:
    """norm(label) -> {uri, preferred_label}. Incluye preferred y alt labels."""
    index: dict[str, dict] = {}
    for _, row in esco.iterrows():
        target = {"esco_uri": row["concept_uri"], "esco_preferred_label": row["preferred_label"]}
        pref = norm(row["preferred_label"])
        if pref:
            index.setdefault(pref, target)
        for alt in str(row["alt_labels"]).split(" | "):
            a = norm(alt)
            if a:
                index.setdefault(a, target)
    return index


# --------------------------------------------------------------------------
# Índice de tokens (para match por inclusión)
# --------------------------------------------------------------------------
def _tokenize(s: str) -> list[str]:
    """Tokens alfanuméricos de un label normalizado: 'Python (computer programming)' -> [python, computer, programming]."""
    return re.findall(r"[a-z0-9]+", norm(s))


def build_token_index(esco: pd.DataFrame):
    """token -> set(posiciones de fila) y nº de tokens por fila (para elegir el label más específico)."""
    token_index: dict[str, set] = {}
    ntokens: list[int] = []
    for i, label in enumerate(esco["preferred_label"].tolist()):
        toks = set(_tokenize(label))
        ntokens.append(len(toks) if toks else 10**6)
        for t in toks:
            token_index.setdefault(t, set()).add(i)
    return token_index, ntokens


# --------------------------------------------------------------------------
# Mapeo genérico (exact -> contains -> fuzzy TF-IDF)
# --------------------------------------------------------------------------
def map_terms_to_esco(
    terms: list[str],
    esco: pd.DataFrame,
    threshold: float = FUZZY_THRESHOLD,
) -> list[dict]:
    """
    Mapea una lista de términos normalizados a ESCO en 3 pasadas, de más a menos estricta:
      1) EXACT:    término == preferredLabel/altLabel.
      2) CONTAINS: TODOS los tokens del término aparecen en un preferredLabel de ESCO
                   (p.ej. 'python' ⊂ 'Python (computer programming)'); se elige el label más
                   específico (menos tokens). Compensa la ausencia de altLabels (harvest full=false).
      3) FUZZY:    TF-IDF de n-gramas de caracteres + coseno (top-1 si supera el umbral).
    Devuelve una fila por término con match_type/uri/label/similarity.
    """
    exact_index = build_exact_index(esco)
    token_index, ntokens = build_token_index(esco)

    esco_labels_norm = esco["preferred_label"].map(norm).tolist()
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
    esco_matrix = vectorizer.fit_transform(esco_labels_norm)

    results: list[dict | None] = [None] * len(terms)
    pending_terms, pending_idx = [], []

    for i, t in enumerate(terms):
        # 1) Exacto
        hit = exact_index.get(t)
        if hit:
            results[i] = {"match_type": "exact", "esco_uri": hit["esco_uri"],
                          "esco_preferred_label": hit["esco_preferred_label"], "similarity": 1.0}
            continue

        # 2) Inclusión de tokens (superset)
        term_tokens = set(_tokenize(t))
        cand: set | None = None
        if term_tokens:
            for tok in term_tokens:
                s = token_index.get(tok)
                if not s:
                    cand = set()
                    break
                cand = set(s) if cand is None else (cand & s)
                if not cand:
                    break
        if cand:
            best = min(cand, key=lambda r: ntokens[r])
            row = esco.iloc[best]
            ratio = round(len(term_tokens) / max(ntokens[best], 1), 4)
            results[i] = {"match_type": "contains", "esco_uri": row["concept_uri"],
                          "esco_preferred_label": row["preferred_label"], "similarity": ratio}
            continue

        # 3) Fuzzy (se resuelve en bloque más abajo)
        pending_terms.append(t)
        pending_idx.append(i)

    if pending_terms:
        q = vectorizer.transform(pending_terms)
        sims = cosine_similarity(q, esco_matrix)  # (n_pending, n_esco)
        best_idx = sims.argmax(axis=1)
        best_sim = sims.max(axis=1)
        for j, i in enumerate(pending_idx):
            sim = float(best_sim[j])
            row = esco.iloc[int(best_idx[j])]
            if sim >= threshold:
                results[i] = {"match_type": "fuzzy", "esco_uri": row["concept_uri"],
                              "esco_preferred_label": row["preferred_label"], "similarity": round(sim, 4)}
            else:
                results[i] = {"match_type": "none", "esco_uri": None, "esco_preferred_label": None,
                              "similarity": round(sim, 4),
                              "best_candidate_below_threshold": row["preferred_label"]}
    return results


# --------------------------------------------------------------------------
# Mapeos concretos del TFG
# --------------------------------------------------------------------------
def map_skills() -> pd.DataFrame:
    inv = load_matchkey_skill_inventory()
    esco_skills = load_esco("skills_en.csv")
    mapped = map_terms_to_esco(inv["matchkey_skill_norm"].tolist(), esco_skills)
    out = pd.concat([inv.reset_index(drop=True), pd.DataFrame(mapped)], axis=1)
    return out


def map_categories() -> pd.DataFrame:
    vac = pd.read_csv(MATCHKEY_DIR / "vacantes.csv")
    cats = (
        vac["category_llm"].dropna().astype(str).map(str.strip)
        .replace("", pd.NA).dropna()
    )
    counts = cats.value_counts()
    cat_df = pd.DataFrame({"category_llm": counts.index, "n_vacantes": counts.values})

    esco_occ = load_esco("occupations_en.csv")
    mapped = map_terms_to_esco([norm(c) for c in cat_df["category_llm"]], esco_occ)
    mapped_df = pd.DataFrame(mapped).rename(
        columns={"esco_uri": "esco_occupation_uri", "esco_preferred_label": "esco_occupation_label"}
    )
    out = pd.concat([cat_df.reset_index(drop=True), mapped_df], axis=1)
    if "isco_code" in esco_occ.columns:
        uri_to_isco = dict(zip(esco_occ["concept_uri"], esco_occ["isco_code"]))
        out["esco_isco_code"] = out["esco_occupation_uri"].map(uri_to_isco)
    return out


def coverage_summary(skills_map: pd.DataFrame, cats_map: pd.DataFrame) -> pd.DataFrame:
    rows = []
    sk = skills_map["match_type"].value_counts()
    n = len(skills_map)
    for mt in ["exact", "contains", "fuzzy", "none"]:
        c = int(sk.get(mt, 0))
        rows.append({"dataset": "skills", "match_type": mt, "n": c, "pct": round(100 * c / n, 1) if n else 0})
    ct = cats_map["match_type"].value_counts()
    nc = len(cats_map)
    for mt in ["exact", "contains", "fuzzy", "none"]:
        c = int(ct.get(mt, 0))
        rows.append({"dataset": "categories", "match_type": mt, "n": c, "pct": round(100 * c / nc, 1) if nc else 0})
    return pd.DataFrame(rows)


def main() -> None:
    print("Mapeando skills de MatchKey contra ESCO...")
    skills_map = map_skills()
    save_csv(skills_map, ESCO_DIR / "matchkey_skills_to_esco.csv")
    print(f"  [OK] matchkey_skills_to_esco.csv: {len(skills_map)} skills únicas")

    print("Mapeando category_llm contra ocupaciones ESCO...")
    cats_map = map_categories()
    save_csv(cats_map, ESCO_DIR / "matchkey_categories_to_esco_occupations.csv")
    print(f"  [OK] matchkey_categories_to_esco_occupations.csv: {len(cats_map)} categorías")

    summary = coverage_summary(skills_map, cats_map)
    save_csv(summary, ESCO_DIR / "_coverage_summary.csv")
    print("\nCobertura del mapeo:")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
