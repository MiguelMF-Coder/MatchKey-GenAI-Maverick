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


def fetch_recommended_jobs(candidate_id):
    """
    Llama a /candidates/{id}/recommended_jobs (GET) para recuperar las vacantes recomendadas.
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/candidates/{candidate_id}/recommended_jobs",
            timeout=15,
        )
    except Exception as e:
        st.error(f"Error al cargar tus vacantes recomendadas: {e}")
        return []

    if resp.status_code == 200:
        data = resp.json()
        # Puede venir como {"jobs": [...]} o directamente lista
        if isinstance(data, dict) and "jobs" in data:
            return data["jobs"]
        if isinstance(data, list):
            return data
        return []
    else:
        st.warning(
            f"No se han podido recuperar tus vacantes recomendadas (código {resp.status_code})."
        )
        return []


def apply_to_job(job_id, candidate_id):
    """
    Llama a /jobs/{job_id}/apply para que el candidato solicite la vacante.
    """
    try:
        resp = requests.post(
            f"{BACKEND_URL}/jobs/{job_id}/apply",
            json={"candidate_id": candidate_id},
            timeout=10,
        )
    except Exception as e:
        st.error(f"Error al solicitar el puesto: {e}")
        return

    if resp.status_code != 200:
        st.error(
            f"No se ha podido solicitar el puesto (código {resp.status_code})."
        )
        return

    data = resp.json()
    msg = data.get("message") if isinstance(data, dict) else "Solicitud enviada correctamente."
    st.success(f"✅ {msg}")


def format_description(text: str) -> str:
    """
    Intenta convertir un tochaco sin saltos de línea en algo legible:
    - Añade párrafos tras cada punto.
    - Mete saltos antes de algunos bloques típicos de JDs (¿Cómo será tu día a día?, Innovación, Be flex...).
    - Convierte bullets que empiezan por '+' en '- ' para markdown.
    """
    if not text:
        return ""

    t = text.replace("\r\n", "\n")

    # Bullets tipo "+ " → "- "
    t = t.replace("+ ", "\n- ")

    # Saltos antes de bloques típicos que suelen ser secciones
    markers = [
        "**¿Cómo será tu día a día?",
        "¿Cómo será tu día a día?",
        "¿Cómo puedes ampliar tus conocimientos?**",
        "¿Cómo puedes ampliar tus conocimientos?",
        "Innovación",
        "Colaboración",
        "Be flex",
    ]
    for m in markers:
        t = t.replace(m, f"\n\n{m}")

    # Párrafos: cada punto seguido se convierte en salto de párrafo
    t = t.replace(". ", ".\n\n")

    return t


# -------------------------
# Render principal de la página
# -------------------------
def render():
    st.markdown("## 💼 Vacantes recomendadas para ti")
    st.caption(
        "Estas vacantes se han generado a partir de tu CV, tus skills y, si la has realizado, "
        "la Llamada IA (motivaciones, valores y encaje de equipo)."
    )

    candidate_id = ensure_candidate_id()
    if not candidate_id:
        st.stop()

    with st.spinner("Buscando vacantes con mejor encaje para ti..."):
        jobs = fetch_recommended_jobs(candidate_id)

    if not jobs:
        st.info(
            "De momento no hay vacantes recomendadas para ti. "
            "Prueba a subir tu CV y completar tu perfil con la Llamada IA para mejorar el matching."
        )
        return

    # Opciones de ordenación simples (cliente)
    st.markdown("### 🔎 Opciones de visualización")
    col_sort, col_filter = st.columns([1, 1])

    with col_sort:
        sort_option = st.selectbox(
            "Ordenar por",
            ["Mejor encaje global", "Encaje por skills", "Encaje por valores"],
        )

    with col_filter:
        st.multiselect(
            "Filtros rápidos (placeholder)",
            ["Remoto", "Híbrido", "Presencial", "Júnior", "Senior"],
            help="Aquí podrás filtrar por tipo de trabajo, modalidad, etc. (a implementar).",
        )

    # Preparamos datos de scores y ordenación
    def extract_scores(job):
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

    # Ordenamos según la opción elegida
    if sort_option == "Mejor encaje global":
        jobs = sorted(
            jobs,
            key=lambda j: extract_scores(j)["global"] or 0,
            reverse=True,
        )
    elif sort_option == "Encaje por skills":
        jobs = sorted(
            jobs,
            key=lambda j: extract_scores(j)["skills"] or 0,
            reverse=True,
        )
    elif sort_option == "Encaje por valores":
        jobs = sorted(
            jobs,
            key=lambda j: extract_scores(j)["values"] or 0,
            reverse=True,
        )

    st.markdown("---")
    st.markdown("### 📋 Lista de vacantes")

    # Renderizamos cada vacante como tarjeta
    for job in jobs:
        job_id = job.get("id") or job.get("job_id")
        title = job.get("title", "Puesto sin título")
        company_name = job.get("company_name") or job.get("company") or "Empresa no indicada"
        location = job.get("location") or "Ubicación no indicada"

        description = job.get("description")
        if description:
            resumen = description[:220] + ("..." if len(description) > 220 else "")
        else:
            resumen = "Sin descripción disponible."

        scores = extract_scores(job)
        global_score = scores["global"]
        skills_score = scores["skills"]
        values_score = scores["values"]
        team_fit_score = scores["team_fit"]

        # Tarjeta
        with st.container():
            st.markdown("---")
            header_col1, header_col2 = st.columns([3, 1])

            with header_col1:
                st.markdown(f"#### {title}")
                st.caption(f"🏢 {company_name}  ·  📍 {location}")

            with header_col2:
                if global_score is not None:
                    st.metric("Encaje global", f"{global_score:.0f} / 100")
                else:
                    st.metric("Encaje global", "N/D")

            st.write(resumen)

            # Subscores
            sub1, sub2, sub3 = st.columns(3)
            with sub1:
                if skills_score is not None:
                    st.progress(min(max(skills_score / 100, 0), 1.0))
                    st.caption(f"Encaje en skills: {skills_score:.0f}/100")
                else:
                    st.caption("Encaje en skills: N/D")

            with sub2:
                if values_score is not None:
                    st.progress(min(max(values_score / 100, 0), 1.0))
                    st.caption(f"Encaje en valores: {values_score:.0f}/100")
                else:
                    st.caption("Encaje en valores: N/D")

            with sub3:
                if team_fit_score is not None:
                    st.progress(min(max(team_fit_score / 100, 0), 1.0))
                    st.caption(f"Encaje en equipo: {team_fit_score:.0f}/100")
                else:
                    st.caption("Encaje en equipo: N/D")

            # Botones de acción
            action_col1, action_col2 = st.columns([1, 1])

            with action_col1:
                if st.button(
                    "🔍 Ver gaps y cómo mejorar para esta vacante",
                    key=f"gaps_{job_id}",
                    use_container_width=True,
                ):
                    st.session_state.selected_job_id = job_id
                    st.session_state.selected_job_title = title
                    st.session_state.current_page = "Mejora (gaps + cursos)"
                    st.rerun()

            with action_col2:
                if st.button(
                    "✅ Solicitar este puesto",
                    key=f"apply_{job_id}",
                    use_container_width=True,
                ):
                    apply_to_job(job_id, candidate_id)

            # Detalles ampliados
            with st.expander("📄 Ver más detalles de la vacante"):
                full_desc = description
                if full_desc:
                    st.markdown("##### Descripción completa")
                    formatted_desc = format_description(full_desc)
                    st.markdown(formatted_desc)
                else:
                    st.write("Sin descripción disponible.")

                st.markdown("##### ℹ️ Información del puesto")
                info_lines = []

                category = job.get("category")
                if category:
                    info_lines.append(f"- **Categoría**: {category}")

                ct_type = job.get("contract_type")
                if ct_type:
                    info_lines.append(f"- **Tipo de contrato**: {ct_type}")

                ct_time = job.get("contract_time")
                if ct_time:
                    info_lines.append(f"- **Jornada**: {ct_time}")

                job_type = job.get("job_type")
                if job_type:
                    info_lines.append(f"- **Modalidad**: {job_type}")

                exp_req = job.get("experience_required")
                if exp_req:
                    info_lines.append(f"- **Experiencia requerida**: {exp_req}")

                edu_req = job.get("education_required")
                if edu_req:
                    info_lines.append(f"- **Formación requerida**: {edu_req}")

                salary_min = job.get("salary_min")
                salary_max = job.get("salary_max")
                if salary_min or salary_max:
                    if salary_min and salary_max:
                        info_lines.append(f"- **Salario**: {salary_min} - {salary_max}")
                    elif salary_min:
                        info_lines.append(f"- **Salario desde**: {salary_min}")
                    elif salary_max:
                        info_lines.append(f"- **Salario hasta**: {salary_max}")

                if info_lines:
                    st.markdown("\n".join(info_lines))
                else:
                    st.write("- Información adicional no disponible.")

                # Tech stack, soft skills, idiomas, beneficios
                tech_stack = job.get("tech_stack") or []
                if isinstance(tech_stack, str):
                    tech_stack = [tech_stack]
                if tech_stack:
                    st.markdown("##### 🛠️ Tech stack")
                    for t in tech_stack:
                        st.write(f"- {t}")

                soft_skills = job.get("soft_skills") or []
                if isinstance(soft_skills, str):
                    soft_skills = [soft_skills]
                if soft_skills:
                    st.markdown("##### 🤝 Soft skills")
                    for s in soft_skills:
                        st.write(f"- {s}")

                languages = job.get("languages") or []
                if isinstance(languages, str):
                    languages = [languages]
                if languages:
                    st.markdown("##### 🌍 Idiomas")
                    for lang in languages:
                        st.write(f"- {lang}")

                benefits = job.get("benefits") or []
                if isinstance(benefits, str):
                    benefits = [benefits]
                if benefits:
                    st.markdown("##### 🎁 Beneficios")
                    for b in benefits:
                        st.write(f"- {b}")

                # Must / Nice (por si en el futuro los tenemos)
                must_have = (
                    job.get("must_have")
                    or job.get("must_skills")
                    or job.get("requirements_must")
                )
                nice_to_have = (
                    job.get("nice_to_have")
                    or job.get("nice_skills")
                    or job.get("requirements_nice")
                )

                if must_have:
                    st.markdown("##### ✅ Requisitos principales (Must-have)")
                    if isinstance(must_have, list):
                        for m in must_have:
                            st.write(f"- {m}")
                    else:
                        st.write(must_have)

                if nice_to_have:
                    st.markdown("##### ⭐ Requisitos valorables (Nice-to-have)")
                    if isinstance(nice_to_have, list):
                        for n in nice_to_have:
                            st.write(f"- {n}")
                    else:
                        st.write(nice_to_have)
