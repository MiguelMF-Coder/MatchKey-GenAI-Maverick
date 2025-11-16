import streamlit as st
import requests
from statistics import mean

BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")


# -------------------------
# Helpers compartidos
# -------------------------
def get_auth_email():
    auth = st.session_state.get("auth", {})
    return auth.get("email")


def ensure_company_id():
    """
    Se asegura de que tengamos un company_id en sesión.
    - Si ya existe en session_state["company_id"], lo devuelve.
    - Si no, llama a /companies/create usando el email del login.
    """
    if "company_id" in st.session_state and st.session_state.company_id is not None:
        return st.session_state.company_id

    email = get_auth_email()
    if not email:
        st.error("No se ha encontrado el email del usuario autenticado.")
        return None

    payload = {"email": email}

    try:
        resp = requests.post(
            f"{BACKEND_URL}/companies/create",
            json=payload,
            timeout=10,
        )
    except Exception as e:
        st.error(f"Error al registrar la empresa en el backend: {e}")
        return None

    if resp.status_code not in (200, 201):
        st.error(
            f"No se ha podido registrar la empresa. Código: {resp.status_code}"
        )
        return None

    data = resp.json()
    company_id = data.get("id") or data.get("company_id")

    if not company_id:
        st.error("El backend no devolvió un company_id válido.")
        return None

    st.session_state.company_id = company_id
    return company_id


def fetch_company_profile(company_id):
    """
    Llama a /companies/{id}/profile (GET) para recuperar datos de la empresa.
    Aquí intentaremos sacar también las vacantes asociadas si el backend las devuelve.
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/companies/{company_id}/profile",
            timeout=10,
        )
    except Exception as e:
        st.error(f"Error al cargar el perfil de empresa: {e}")
        return None

    if resp.status_code == 200:
        return resp.json()
    else:
        st.warning(
            f"No se ha podido cargar el perfil de empresa (código {resp.status_code})."
        )
        return None


def fetch_company_jobs(company_id):
    """
    Intenta obtener las vacantes de la empresa.
    Por ahora usamos /companies/{id}/profile y buscamos claves típicas:
      - "jobs"
      - "open_jobs"
    Ajusta esta función cuando tengas un endpoint específico para listar jobs de una empresa.
    """
    profile_data = fetch_company_profile(company_id) or {}
    jobs = (
        profile_data.get("jobs")
        or profile_data.get("open_jobs")
        or []
    )

    if not isinstance(jobs, list):
        return []

    return jobs


def fetch_match_candidates(job_id):
    """
    Llama a /jobs/{id}/match_candidates (GET) para recuperar los candidatos
    y sus scores para una vacante concreta.
    Asumimos que puede devolver:
      - una lista directamente
      - o un dict con clave "candidates".
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/jobs/{job_id}/match_candidates",
            timeout=20,
        )
    except Exception as e:
        st.error(f"Error al obtener el matching de candidatos para esta vacante: {e}")
        return []

    if resp.status_code != 200:
        st.error(
            f"No se ha podido obtener la información de matching (código {resp.status_code})."
        )
        try:
            st.json(resp.json())
        except Exception:
            st.write(resp.text)
        return []

    data = resp.json()
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "candidates" in data:
        return data["candidates"]
    return []


def extract_scores(match_item):
    """
    Extrae scores de un item de matching candidato-vacante.
    Soporta varias estructuras posibles:
      - match_item["scores"]["global"/"skills"/"values"/"team_fit"]
      - match_item["global_score"], match_item["skills_match"], etc.
    """
    scores = match_item.get("scores", {}) or {}

    global_score = (
        scores.get("global")
        or scores.get("global_score")
        or match_item.get("global_score")
    )
    skills_score = (
        scores.get("skills")
        or scores.get("skills_match")
        or match_item.get("skills_match")
    )
    values_score = (
        scores.get("values")
        or scores.get("values_match")
        or match_item.get("values_match")
    )
    team_fit_score = (
        scores.get("team_fit")
        or scores.get("teamfit")
        or match_item.get("team_fit")
    )

    return {
        "global": global_score,
        "skills": skills_score,
        "values": values_score,
        "team_fit": team_fit_score,
    }


# -------------------------
# Render principal de la página
# -------------------------
def render():
    st.markdown("## 📈 Analítica de talento")
    st.caption(
        "Analiza cómo encajan los candidatos con tus vacantes: distribución de matching, "
        "fortalezas, gaps y oportunidades de mejora."
    )

    company_id = ensure_company_id()
    if not company_id:
        st.stop()

    # Obtenemos las vacantes de la empresa
    with st.spinner("Cargando tus vacantes..."):
        jobs = fetch_company_jobs(company_id)

    if not jobs:
        st.info(
            "Todavía no hay vacantes asociadas a esta empresa o el backend no las devuelve en el perfil. "
            "Crea al menos una vacante desde **'Crear vacante'** para poder ver analíticas."
        )
        if st.button("Ir a crear vacante", use_container_width=True):
            st.session_state.current_page = "Crear vacante"
            st.experimental_rerun()
        return

    # Construimos opciones para el selector
    job_options = {}
    for job in jobs:
        job_id = job.get("id") or job.get("job_id")
        title = job.get("title", "Puesto sin título")
        location = job.get("location") or ""
        label = f"{title} (ID: {job_id})"
        if location:
            label += f" · {location}"
        if job_id is not None:
            job_options[label] = job_id

    if not job_options:
        st.warning(
            "No hemos podido identificar IDs de las vacantes. Revisa el formato devuelto por el backend."
        )
        return

    st.markdown("### 🎯 Selecciona una vacante para analizar")

    selected_label = st.selectbox(
        "Vacante",
        options=list(job_options.keys()),
    )
    selected_job_id = job_options[selected_label]

    st.markdown(f"Analizando vacante: **{selected_label}**")

    # Obtenemos matching de candidatos para esa vacante
    with st.spinner("Calculando analítica de matching para esta vacante..."):
        matches = fetch_match_candidates(selected_job_id)

    if not matches:
        st.info(
            "Todavía no hay candidatos matcheados con esta vacante o el backend no devuelve resultados. "
            "Cuando haya candidatos, verás aquí su distribución de encaje."
        )
        return

    # -------------------------
    # Procesamos scores
    # -------------------------
    global_scores = []
    skills_scores = []
    values_scores = []
    team_fit_scores = []

    processed_matches = []
    for m in matches:
        scores = extract_scores(m)
        global_scores.append(scores["global"]) if scores["global"] is not None else None
        skills_scores.append(scores["skills"]) if scores["skills"] is not None else None
        values_scores.append(scores["values"]) if scores["values"] is not None else None
        team_fit_scores.append(scores["team_fit"]) if scores["team_fit"] is not None else None

        processed_matches.append(
            {
                "raw": m,
                "scores": scores,
            }
        )

    # -------------------------
    # Fila 1: métricas agregadas
    # -------------------------
    st.markdown("### 📊 Resumen de encaje para esta vacante")

    col1, col2, col3, col4 = st.columns(4)

    def _avg(values_list):
        values_list = [v for v in values_list if isinstance(v, (int, float))]
        return int(mean(values_list)) if values_list else None

    avg_global = _avg(global_scores)
    avg_skills = _avg(skills_scores)
    avg_values = _avg(values_scores)
    avg_team_fit = _avg(team_fit_scores)

    with col1:
        if avg_global is not None:
            st.metric("Media encaje global", f"{avg_global} / 100")
        else:
            st.metric("Media encaje global", "N/D")

    with col2:
        if avg_skills is not None:
            st.metric("Media encaje skills", f"{avg_skills} / 100")
        else:
            st.metric("Media encaje skills", "N/D")

    with col3:
        if avg_values is not None:
            st.metric("Media encaje valores", f"{avg_values} / 100")
        else:
            st.metric("Media encaje valores", "N/D")

    with col4:
        if avg_team_fit is not None:
            st.metric("Media team-fit", f"{avg_team_fit} / 100")
        else:
            st.metric("Media team-fit", "N/D")

    st.caption(f"Número de candidatos analizados: {len(processed_matches)}")

    st.markdown("---")

    # -------------------------
    # Fila 2: distribución simple de encajes
    # -------------------------
    st.markdown("### 📈 Distribución de encaje global")

    high = len([g for g in global_scores if isinstance(g, (int, float)) and g >= 80])
    mid = len([g for g in global_scores if isinstance(g, (int, float)) and 60 <= g < 80])
    low = len([g for g in global_scores if isinstance(g, (int, float)) and g < 60])

    col_h, col_m, col_l = st.columns(3)
    with col_h:
        st.markdown("#### 🔝 > 80/100")
        st.write(f"{high} candidatos")
    with col_m:
        st.markdown("#### 🙂 60–79/100")
        st.write(f"{mid} candidatos")
    with col_l:
        st.markdown("#### ⚠️ < 60/100")
        st.write(f"{low} candidatos")

    st.markdown("---")

    # -------------------------
    # Top candidatos por encaje global
    # -------------------------
    st.markdown("### 🏅 Top candidatos por encaje global")

    # Ordenamos por encaje global
    processed_matches_sorted = sorted(
        processed_matches,
        key=lambda x: x["scores"]["global"] if x["scores"]["global"] is not None else 0,
        reverse=True,
    )
    top_matches = processed_matches_sorted[:5]

    for idx, item in enumerate(top_matches, start=1):
        m = item["raw"]
        scores = item["scores"]

        candidate = m.get("candidate") or {}
        candidate_id = candidate.get("id") or m.get("candidate_id")
        candidate_name = (
            candidate.get("name")
            or candidate.get("full_name")
            or f"Candidato {candidate_id}"
            or "Candidato sin nombre"
        )
        candidate_email = candidate.get("email")

        with st.container():
            st.markdown(f"#### {idx}. {candidate_name}")
            if candidate_email:
                st.caption(f"📧 {candidate_email}")
            if candidate_id:
                st.caption(f"ID candidato: {candidate_id}")

            col_s1, col_s2, col_s3, col_s4 = st.columns(4)

            with col_s1:
                if scores["global"] is not None:
                    st.write(f"Global: {scores['global']:.0f}/100")
                else:
                    st.write("Global: N/D")

            with col_s2:
                if scores["skills"] is not None:
                    st.write(f"Skills: {scores['skills']:.0f}/100")
                else:
                    st.write("Skills: N/D")

            with col_s3:
                if scores["values"] is not None:
                    st.write(f"Valores: {scores['values']:.0f}/100")
                else:
                    st.write("Valores: N/D")

            with col_s4:
                if scores["team_fit"] is not None:
                    st.write(f"Team-fit: {scores['team_fit']:.0f}/100")
                else:
                    st.write("Team-fit: N/D")

            with st.expander("Ver detalle técnico del matching para este candidato"):
                st.json(m)

            st.markdown("---")

    # -------------------------
    # Bloque de insights básicos (texto)
    # -------------------------
    st.markdown("### 💡 Insights básicos (versión inicial)")

    insights = []

    if avg_global is not None:
        if avg_global >= 75:
            insights.append(
                "El encaje global medio es **alto**. La vacante parece bien definida y alineada con los candidatos que atraes."
            )
        elif avg_global >= 60:
            insights.append(
                "El encaje global medio es **razonable**, pero hay margen de mejora. "
                "Revisa requisitos Must-Have y descripción para afinar el perfil objetivo."
            )
        else:
            insights.append(
                "El encaje global medio es **bajo**. Puede que la vacante esté pidiendo skills poco frecuentes "
                "o que la descripción no esté atrayendo al tipo de perfil deseado."
            )

    if avg_skills is not None and avg_values is not None:
        if avg_skills > avg_values:
            insights.append(
                "Tus candidatos encajan mejor en **skills** que en **valores**. "
                "Quizá convenga reforzar la parte de cultura y valores en el proceso de selección."
            )
        elif avg_values > avg_skills:
            insights.append(
                "Tus candidatos encajan mejor en **valores** que en **skills**. "
                "Podría ser interesante flexibilizar algunos requisitos técnicos o potenciar formación."
            )

    if avg_team_fit is not None:
        if avg_team_fit < 60:
            insights.append(
                "El **team-fit** medio es bajo. Revisa la definición del equipo (en la creación de vacante) "
                "y asegúrate de que refleja bien cómo trabaja realmente el equipo."
            )

    if not insights:
        insights.append(
            "Cuando haya más datos de candidatos y se estabilicen los scores, aquí aparecerán recomendaciones "
            "sobre cómo mejorar el matching."
        )

    for ins in insights:
        st.write(f"- {ins}")
