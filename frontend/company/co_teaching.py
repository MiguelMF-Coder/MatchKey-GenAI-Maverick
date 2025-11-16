import streamlit as st
import requests

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
    Lo usamos para inferir las vacantes relacionadas.
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
        return None


def fetch_company_jobs(company_id):
    """
    Intenta obtener las vacantes de la empresa a partir del perfil.
    Busca claves típicas:
      - "jobs"
      - "open_jobs"
    Ajusta cuando tengas un endpoint específico para listar jobs de una empresa.
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


def fetch_co_teaching_pairs(job_id):
    """
    Llama a /jobs/{id}/co_teaching (GET) para recuperar las parejas recomendadas.
    Formatos posibles:
      - lista directamente
      - dict con clave "pairs"
    Cada pareja puede tener:
      - candidate_a, candidate_b
      - coverage / pair_coverage
      - risk / pair_risk
      - score / global_score
      - notes / explanation / complementarities
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/jobs/{job_id}/co_teaching",
            timeout=20,
        )
    except Exception as e:
        st.error(f"Error al obtener recomendaciones de Co-Teaching: {e}")
        return []

    if resp.status_code != 200:
        st.error(
            f"No se ha podido obtener la información de Co-Teaching (código {resp.status_code})."
        )
        try:
            st.json(resp.json())
        except Exception:
            st.write(resp.text)
        return []

    data = resp.json()
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "pairs" in data:
        return data["pairs"]
    return []


# -------------------------
# Render principal de la página
# -------------------------
def render():
    st.markdown("## 🤝 Co-Teaching")
    st.caption(
        "Explora parejas de candidatos que, juntos, cubren mejor los requisitos de una vacante "
        "que de forma individual."
    )

    company_id = ensure_company_id()
    if not company_id:
        st.stop()

    with st.spinner("Cargando tus vacantes..."):
        jobs = fetch_company_jobs(company_id)

    if not jobs:
        st.info(
            "Todavía no hay vacantes asociadas a esta empresa o el backend no las devuelve en el perfil. "
            "Crea al menos una vacante desde **'Crear vacante'** para poder usar Co-Teaching."
        )
        if st.button("Ir a crear vacante", use_container_width=True):
            st.session_state.current_page = "Crear vacante"
            st.experimental_rerun()
        return

    # Selector de vacante
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
            "No hemos podido identificar IDs de las vacantes. "
            "Revisa el formato devuelto por el backend."
        )
        return

    st.markdown("### 🎯 Selecciona una vacante para ver parejas recomendadas")

    selected_label = st.selectbox(
        "Vacante",
        options=list(job_options.keys()),
    )
    selected_job_id = job_options[selected_label]

    st.markdown(f"Analizando Co-Teaching para: **{selected_label}**")

    # Obtener parejas
    with st.spinner("Buscando parejas de candidatos complementarios..."):
        pairs = fetch_co_teaching_pairs(selected_job_id)

    if not pairs:
        st.info(
            "Por ahora no hay parejas recomendadas para esta vacante o el backend no devuelve resultados. "
            "Cuando el motor de Co-Teaching esté activo, verás aquí las combinaciones sugeridas."
        )
        return

    st.markdown("---")
    st.markdown("### 🧩 Parejas recomendadas")

    for idx, pair in enumerate(pairs, start=1):
        # Parsing defensivo
        candidate_a = pair.get("candidate_a") or pair.get("a") or {}
        candidate_b = pair.get("candidate_b") or pair.get("b") or {}

        a_id = candidate_a.get("id") or candidate_a.get("candidate_id")
        b_id = candidate_b.get("id") or candidate_b.get("candidate_id")

        a_name = (
            candidate_a.get("name")
            or candidate_a.get("full_name")
            or f"Candidato {a_id}"
            or "Candidato A"
        )
        b_name = (
            candidate_b.get("name")
            or candidate_b.get("full_name")
            or f"Candidato {b_id}"
            or "Candidato B"
        )

        coverage = (
            pair.get("coverage")
            or pair.get("pair_coverage")
            or pair.get("coverage_score")
        )
        risk = (
            pair.get("risk")
            or pair.get("pair_risk")
        )
        global_score = (
            pair.get("global_score")
            or pair.get("score")
        )

        complementarities = (
            pair.get("complementarities")
            or pair.get("notes")
            or pair.get("explanation")
        )

        a_strong_skills = (
            candidate_a.get("strong_skills")
            or candidate_a.get("skills_strong")
            or []
        )
        b_strong_skills = (
            candidate_b.get("strong_skills")
            or candidate_b.get("skills_strong")
            or []
        )

        with st.container():
            st.markdown(f"#### 🧑‍🤝‍🧑 Pareja {idx}: {a_name} + {b_name}")

            # Scores resumen
            col1, col2, col3 = st.columns(3)
            with col1:
                if coverage is not None:
                    st.metric("Cobertura conjunta", f"{coverage:.0f} / 100")
                else:
                    st.metric("Cobertura conjunta", "N/D")
            with col2:
                if risk is not None:
                    st.metric("Riesgo de la pareja", f"{risk:.0f} / 100")
                else:
                    st.metric("Riesgo de la pareja", "N/D")
            with col3:
                if global_score is not None:
                    st.metric("Score global pareja", f"{global_score:.0f} / 100")
                else:
                    st.metric("Score global pareja", "N/D")

            st.markdown("##### 💼 ¿Qué aporta cada uno?")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**{a_name}**")
                if a_strong_skills:
                    if isinstance(a_strong_skills, list):
                        st.write("Skills fuertes: " + ", ".join(a_strong_skills))
                    else:
                        st.write(f"Skills fuertes: {a_strong_skills}")
                else:
                    st.caption("No hay detalle de skills fuertes devuelto por el backend.")

            with c2:
                st.markdown(f"**{b_name}**")
                if b_strong_skills:
                    if isinstance(b_strong_skills, list):
                        st.write("Skills fuertes: " + ", ".join(b_strong_skills))
                    else:
                        st.write(f"Skills fuertes: {b_strong_skills}")
                else:
                    st.caption("No hay detalle de skills fuertes devuelto por el backend.")

            if complementarities:
                st.markdown("##### 🔍 Por qué esta pareja tiene sentido")
                if isinstance(complementarities, list):
                    for c in complementarities:
                        st.write(f"- {c}")
                else:
                    st.write(complementarities)

            # Expander técnico para debug / detalle
            with st.expander("Ver detalle técnico devuelto por el motor de Co-Teaching"):
                st.json(pair)

            st.markdown("---")
import streamlit as st
import requests

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
    Lo usamos para inferir las vacantes relacionadas.
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
        return None


def fetch_company_jobs(company_id):
    """
    Intenta obtener las vacantes de la empresa a partir del perfil.
    Busca claves típicas:
      - "jobs"
      - "open_jobs"
    Ajusta cuando tengas un endpoint específico para listar jobs de una empresa.
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


def fetch_co_teaching_pairs(job_id):
    """
    Llama a /jobs/{id}/co_teaching (GET) para recuperar las parejas recomendadas.
    Formatos posibles:
      - lista directamente
      - dict con clave "pairs"
    Cada pareja puede tener:
      - candidate_a, candidate_b
      - coverage / pair_coverage
      - risk / pair_risk
      - score / global_score
      - notes / explanation / complementarities
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/jobs/{job_id}/co_teaching",
            timeout=20,
        )
    except Exception as e:
        st.error(f"Error al obtener recomendaciones de Co-Teaching: {e}")
        return []

    if resp.status_code != 200:
        st.error(
            f"No se ha podido obtener la información de Co-Teaching (código {resp.status_code})."
        )
        try:
            st.json(resp.json())
        except Exception:
            st.write(resp.text)
        return []

    data = resp.json()
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "pairs" in data:
        return data["pairs"]
    return []


# -------------------------
# Render principal de la página
# -------------------------
def render():
    st.markdown("## 🤝 Co-Teaching")
    st.caption(
        "Explora parejas de candidatos que, juntos, cubren mejor los requisitos de una vacante "
        "que de forma individual."
    )

    company_id = ensure_company_id()
    if not company_id:
        st.stop()

    with st.spinner("Cargando tus vacantes..."):
        jobs = fetch_company_jobs(company_id)

    if not jobs:
        st.info(
            "Todavía no hay vacantes asociadas a esta empresa o el backend no las devuelve en el perfil. "
            "Crea al menos una vacante desde **'Crear vacante'** para poder usar Co-Teaching."
        )
        if st.button("Ir a crear vacante", use_container_width=True):
            st.session_state.current_page = "Crear vacante"
            st.experimental_rerun()
        return

    # Selector de vacante
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
            "No hemos podido identificar IDs de las vacantes. "
            "Revisa el formato devuelto por el backend."
        )
        return

    st.markdown("### 🎯 Selecciona una vacante para ver parejas recomendadas")

    selected_label = st.selectbox(
        "Vacante",
        options=list(job_options.keys()),
    )
    selected_job_id = job_options[selected_label]

    st.markdown(f"Analizando Co-Teaching para: **{selected_label}**")

    # Obtener parejas
    with st.spinner("Buscando parejas de candidatos complementarios..."):
        pairs = fetch_co_teaching_pairs(selected_job_id)

    if not pairs:
        st.info(
            "Por ahora no hay parejas recomendadas para esta vacante o el backend no devuelve resultados. "
            "Cuando el motor de Co-Teaching esté activo, verás aquí las combinaciones sugeridas."
        )
        return

    st.markdown("---")
    st.markdown("### 🧩 Parejas recomendadas")

    for idx, pair in enumerate(pairs, start=1):
        # Parsing defensivo
        candidate_a = pair.get("candidate_a") or pair.get("a") or {}
        candidate_b = pair.get("candidate_b") or pair.get("b") or {}

        a_id = candidate_a.get("id") or candidate_a.get("candidate_id")
        b_id = candidate_b.get("id") or candidate_b.get("candidate_id")

        a_name = (
            candidate_a.get("name")
            or candidate_a.get("full_name")
            or f"Candidato {a_id}"
            or "Candidato A"
        )
        b_name = (
            candidate_b.get("name")
            or candidate_b.get("full_name")
            or f"Candidato {b_id}"
            or "Candidato B"
        )

        coverage = (
            pair.get("coverage")
            or pair.get("pair_coverage")
            or pair.get("coverage_score")
        )
        risk = (
            pair.get("risk")
            or pair.get("pair_risk")
        )
        global_score = (
            pair.get("global_score")
            or pair.get("score")
        )

        complementarities = (
            pair.get("complementarities")
            or pair.get("notes")
            or pair.get("explanation")
        )

        a_strong_skills = (
            candidate_a.get("strong_skills")
            or candidate_a.get("skills_strong")
            or []
        )
        b_strong_skills = (
            candidate_b.get("strong_skills")
            or candidate_b.get("skills_strong")
            or []
        )

        with st.container():
            st.markdown(f"#### 🧑‍🤝‍🧑 Pareja {idx}: {a_name} + {b_name}")

            # Scores resumen
            col1, col2, col3 = st.columns(3)
            with col1:
                if coverage is not None:
                    st.metric("Cobertura conjunta", f"{coverage:.0f} / 100")
                else:
                    st.metric("Cobertura conjunta", "N/D")
            with col2:
                if risk is not None:
                    st.metric("Riesgo de la pareja", f"{risk:.0f} / 100")
                else:
                    st.metric("Riesgo de la pareja", "N/D")
            with col3:
                if global_score is not None:
                    st.metric("Score global pareja", f"{global_score:.0f} / 100")
                else:
                    st.metric("Score global pareja", "N/D")

            st.markdown("##### 💼 ¿Qué aporta cada uno?")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**{a_name}**")
                if a_strong_skills:
                    if isinstance(a_strong_skills, list):
                        st.write("Skills fuertes: " + ", ".join(a_strong_skills))
                    else:
                        st.write(f"Skills fuertes: {a_strong_skills}")
                else:
                    st.caption("No hay detalle de skills fuertes devuelto por el backend.")

            with c2:
                st.markdown(f"**{b_name}**")
                if b_strong_skills:
                    if isinstance(b_strong_skills, list):
                        st.write("Skills fuertes: " + ", ".join(b_strong_skills))
                    else:
                        st.write(f"Skills fuertes: {b_strong_skills}")
                else:
                    st.caption("No hay detalle de skills fuertes devuelto por el backend.")

            if complementarities:
                st.markdown("##### 🔍 Por qué esta pareja tiene sentido")
                if isinstance(complementarities, list):
                    for c in complementarities:
                        st.write(f"- {c}")
                else:
                    st.write(complementarities)

            # Expander técnico para debug / detalle
            with st.expander("Ver detalle técnico devuelto por el motor de Co-Teaching"):
                st.json(pair)

            st.markdown("---")
