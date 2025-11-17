import streamlit as st
import requests
from utils import get_backend_url

BACKEND_URL = get_backend_url()

# -------------------------
# Helpers compartidos
# -------------------------
def get_auth_email():
    auth = st.session_state.get("auth", {})
    return auth.get("email")


def ensure_candidate_id():
    """
    Se asegura de que tengamos un candidate_id en sesión.
    - Si ya existe en session_state["candidate_id"], lo devuelve.
    - Si no, llama a /candidates/create usando el email del login.
    """
    if "candidate_id" in st.session_state and st.session_state.candidate_id is not None:
        return st.session_state.candidate_id

    email = get_auth_email()
    if not email:
        st.error("No se ha encontrado el email del usuario autenticado.")
        return None

    payload = {"email": email}

    try:
        resp = requests.post(
            f"{BACKEND_URL}/candidates/create",
            json=payload,
            timeout=10,
        )
    except Exception as e:
        st.error(f"Error al crear el candidato en el backend: {e}")
        return None

    if resp.status_code not in (200, 201):
        st.error(
            f"No se ha podido registrar el candidato. Código: {resp.status_code}"
        )
        return None

    data = resp.json()
    candidate_id = data.get("id") or data.get("candidate_id")

    if not candidate_id:
        st.error("El backend no devolvió un candidate_id válido.")
        return None

    st.session_state.candidate_id = candidate_id
    return candidate_id


def fetch_candidate_profile(candidate_id):
    """
    Llama a /candidates/{id}/profile (GET) para recuperar los datos actuales.
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/candidates/{candidate_id}/profile",
            timeout=10,
        )
    except Exception as e:
        st.error(f"Error al cargar tu perfil: {e}")
        return None

    if resp.status_code == 200:
        return resp.json()
    else:
        return None


def fetch_recommended_jobs(candidate_id):
    """
    Llama a /candidates/{id}/recommended_jobs (GET) para recuperar las vacantes recomendadas.
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/candidates/{candidate_id}/recommended_jobs",
            timeout=10,
        )
    except Exception as e:
        st.error(f"Error al cargar tus vacantes recomendadas: {e}")
        return []

    if resp.status_code == 200:
        data = resp.json()
        if isinstance(data, dict) and "jobs" in data:
            return data["jobs"]
        if isinstance(data, list):
            return data
        return []
    return []


def extract_scores_from_job(job):
    scores = job.get("scores", {}) or {}
    global_score = (
        scores.get("global")
        or scores.get("global_score")
        or job.get("global_score")
    )
    skills_score = (
        scores.get("skills")
        or scores.get("skills_match")
        or job.get("skills_match")
    )
    values_score = (
        scores.get("values")
        or scores.get("values_match")
        or job.get("values_match")
    )
    team_fit_score = (
        scores.get("team_fit")
        or scores.get("teamfit")
        or job.get("team_fit")
    )

    return {
        "global": global_score,
        "skills": skills_score,
        "values": values_score,
        "team_fit": team_fit_score,
    }


# -------------------------
# Render principal del dashboard
# -------------------------
def render():
    st.markdown("## 📊 Dashboard candidato")
    st.caption(
        "Resumen rápido de tu perfil, tu progreso y cómo encajas con las vacantes recomendadas."
    )

    candidate_id = ensure_candidate_id()
    if not candidate_id:
        st.stop()

    # Cargamos datos básicos en paralelo
    profile_data = fetch_candidate_profile(candidate_id) or {}
    jobs = fetch_recommended_jobs(candidate_id)

    # Datos de perfil
    name = profile_data.get("name") or get_auth_email() or "Tu perfil"
    headline = profile_data.get("headline", "")
    skills = profile_data.get("skills") or profile_data.get("all_skills") or []
    num_skills = len(skills)

    # Intentamos detectar si hay info de HR Copilot
    hr_section = (
        profile_data.get("hr_copilot")
        or profile_data.get("psychological_profile")
        or {}
    )
    has_hr_data = bool(
        hr_section
        or profile_data.get("motivaciones")
        or profile_data.get("valores_detectados")
        or profile_data.get("soft_skills")
    )

    # -------------------------
    # Fila 1: tarjetas resumen
    # -------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 👤 Estado de tu perfil")
        st.write(f"**Nombre:** {name}")
        if headline:
            st.write(f"**Titular:** {headline}")
        st.write(f"**Skills detectados:** {num_skills}")

        if num_skills == 0:
            st.warning(
                "Todavía no se han detectado skills en tu perfil. "
                "Sube tu CV desde la sección **Mi perfil**."
            )
        else:
            st.caption("Puedes actualizar tus datos en la sección **Mi perfil**.")

    with col2:
        st.markdown("#### 🎙️ Llamada IA (HR Copilot)")
        if has_hr_data:
            st.success("Llamada IA realizada y perfil enriquecido ✅")
            st.caption(
                "Ya se han detectado motivaciones, valores y soft skills. "
                "Puedes volver a ver el detalle en **Llamada IA**."
            )
        else:
            st.info(
                "Aún no has completado la Llamada IA o no hay datos guardados. "
                "Te recomendamos hacerlo para mejorar el matching."
            )

        if st.button("Ir a Llamada IA", use_container_width=True):
            st.session_state.current_page = "Llamada IA"
            st.rerun()

    with col3:
        st.markdown("#### 💼 Vacantes recomendadas")
        num_jobs = len(jobs)
        st.write(f"**Vacantes encontradas:** {num_jobs}")

        if num_jobs > 0:
            # Mejor encaje global
            jobs_sorted = sorted(
                jobs,
                key=lambda j: extract_scores_from_job(j)["global"] or 0,
                reverse=True,
            )
            best_job = jobs_sorted[0]
            best_scores = extract_scores_from_job(best_job)
            best_title = best_job.get("title", "Vacante con mejor encaje")
            best_company = (
                best_job.get("company_name")
                or best_job.get("company")
                or "Empresa no indicada"
            )

            st.markdown("**Mejor encaje actual:**")
            st.write(f"- {best_title} · {best_company}")
            if best_scores["global"] is not None:
                st.write(f"- Encaje global: {best_scores['global']:.0f}/100")
        else:
            st.caption(
                "Cuando tengas más información en tu perfil, aquí aparecerán vacantes recomendadas."
            )

        if st.button("Ver vacantes recomendadas", use_container_width=True):
            st.session_state.current_page = "Vacantes recomendadas"
            st.rerun()

    st.markdown("---")

    # -------------------------
    # Fila 2: detalle rápido de perfil + top vacantes
    # -------------------------
    left, right = st.columns([2, 2])

    with left:
        st.markdown("### 🧩 Resumen rápido de tu perfil")

        if skills:
            st.markdown("**Algunas de tus skills detectadas:**")
            # mostramos solo las primeras 12 para no saturar
            preview = skills[:12]
            st.write(", ".join(preview))
            if len(skills) > 12:
                st.caption(f"...y {len(skills) - 12} más.")

        else:
            st.caption(
                "Todavía no hay skills detectadas. Sube tu CV en **Mi perfil** para que el sistema las extraiga."
            )

        # Un pequeño bloque para motivaciones/valores si existen
        motivaciones = (
            profile_data.get("motivaciones")
            or hr_section.get("motivaciones")
        )
        valores = (
            profile_data.get("valores_detectados")
            or hr_section.get("valores_detectados")
        )

        if motivaciones or valores:
            st.markdown("**Información de la Llamada IA:**")
            if motivaciones:
                st.write(f"- Motivaciones: {motivaciones}")
            if valores:
                if isinstance(valores, list):
                    st.write(f"- Valores detectados: {', '.join(valores)}")
                else:
                    st.write(f"- Valores detectados: {valores}")
        else:
            st.caption(
                "Cuando realices la Llamada IA, aquí aparecerá un resumen de tus motivaciones y valores."
            )

    with right:
        st.markdown("### 🔝 Top 3 vacantes por encaje global")

        if not jobs:
            st.caption(
                "Aún no hay vacantes suficientes para mostrar un ranking. "
                "Vuelve más tarde o revisa que tu perfil esté actualizado."
            )
        else:
            jobs_sorted = sorted(
                jobs,
                key=lambda j: extract_scores_from_job(j)["global"] or 0,
                reverse=True,
            )
            top_jobs = jobs_sorted[:3]

            for job in top_jobs:
                job_id = job.get("id") or job.get("job_id")
                title = job.get("title", "Puesto sin título")
                company_name = (
                    job.get("company_name")
                    or job.get("company")
                    or "Empresa no indicada"
                )
                scores = extract_scores_from_job(job)
                global_score = scores["global"]

                with st.container():
                    st.markdown(f"**{title}**")
                    st.caption(f"🏢 {company_name}")
                    if global_score is not None:
                        st.write(f"Encaje global: {global_score:.0f}/100")
                    else:
                        st.write("Encaje global: N/D")

                    if st.button(
                        "Ver gaps para esta vacante",
                        key=f"dash_gaps_{job_id}",
                    ):
                        st.session_state.selected_job_id = job_id
                        st.session_state.selected_job_title = title
                        st.session_state.current_page = "Mejora (gaps + cursos)"
                        st.rerun()
                    st.markdown("---")