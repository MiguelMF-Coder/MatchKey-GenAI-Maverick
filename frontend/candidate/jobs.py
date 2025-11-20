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


def fetch_match_scores(candidate_id: int, job_id: int):
    """
    Llama al backend para obtener los scores reales de matching
    para (candidate_id, job_id).

    Endpoint: GET /matching/candidates/{candidate_id}/job/{job_id}/scores

    Esperamos algo como:
    {
        "skills_fit": 80.0,
        "values_fit": 70.0,
        "team_fit": 65.0,
        "global_fit": 75.0
    }
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/matching/candidates/{candidate_id}/job/{job_id}/scores",
            timeout=10,
        )
    except Exception as e:
        st.warning(f"No se han podido cargar los scores para la vacante {job_id}: {e}")
        return None

    if resp.status_code != 200:
        return None

    data = resp.json() or {}

    # Normalizamos nombres para que el resto del código viva tranquilo
    skills_fit = data.get("skills_fit") or data.get("skills_score")
    values_fit = data.get("values_fit") or data.get("values_score")
    team_fit = data.get("team_fit") or data.get("teamfit") or data.get("team_fit_score")
    global_fit = data.get("global_fit") or data.get("global_score")

    return {
        # nombres consistentes internos
        "skills_fit": skills_fit,
        "values_fit": values_fit,
        "team_fit": team_fit,
        "global_fit": global_fit,
    }


def fetch_recommended_jobs(candidate_id):
    """
    1) Llama a /candidates/{id}/recommended_jobs para sacar las vacantes base.
    2) Para cada vacante, llama a /matching/candidates/{id}/job/{job_id}/scores
       y mete los scores normalizados en job["scores"].
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/candidates/{candidate_id}/recommended_jobs",
            timeout=15,
        )
    except Exception as e:
        st.error(f"Error al cargar tus vacantes recomendadas: {e}")
        return []

    if resp.status_code != 200:
        st.warning(
            f"No se han podido recuperar tus vacantes recomendadas "
            f"(código {resp.status_code})."
        )
        return []

    data = resp.json()
    if isinstance(data, dict) and "jobs" in data:
        jobs = data["jobs"]
    elif isinstance(data, list):
        jobs = data
    else:
        jobs = []

    # Enriquecemos cada job con sus scores en tiempo real
    for job in jobs:
        job_id = job.get("id") or job.get("job_id")
        if not job_id:
            continue

        scores = fetch_match_scores(candidate_id, job_id)
        if not scores:
            # si no hay scores, dejamos todo a 0
            job["scores"] = {
                "skills_match": 0.0,
                "values_match": 0.0,
                "team_fit": 0.0,
                "global_score": 0.0,
            }
            continue

        skills_fit = scores.get("skills_fit") or 0.0
        values_fit = scores.get("values_fit") or 0.0
        team_fit = scores.get("team_fit") or 0.0
        global_fit = scores.get("global_fit") or 0.0

        # Dejamos los nombres alineados con extract_scores
        job["scores"] = {
            # nombres “nuevos”
            "skills_match": skills_fit,
            "values_match": values_fit,
            "team_fit": team_fit,
            "global_score": global_fit,
            # alias por compatibilidad
            "skills_fit": skills_fit,
            "values_fit": values_fit,
            "global_fit": global_fit,
        }

    return jobs


def extract_scores(job: dict) -> dict:
    """
    Lee job["scores"] y devuelve un diccionario limpio y completo
    con todos los alias necesarios.
    """
    scores = job.get("scores") or {}

    # Skills
    skills_match = scores.get("skills_match")
    if skills_match is None:
        skills_match = scores.get("skills_fit", 0.0)

    # Values
    values_match = scores.get("values_match")
    if values_match is None:
        values_match = scores.get("values_fit", 0.0)

    # Team
    team_fit = scores.get("team_fit", 0.0)

    # Global
    global_score = scores.get("global_score")
    if global_score is None:
        global_score = scores.get("global_fit", 0.0)

    return {
        # nombres “nuevos”
        "skills_match": skills_match,
        "values_match": values_match,
        "team_fit": team_fit,
        "global_score": global_score,
        # alias para código antiguo
        "skills_fit": skills_match,
        "values_fit": values_match,
        "global_fit": global_score,
    }


def apply_to_job(job_id, candidate_id):
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
    if not text:
        return ""

    t = text.replace("\r\n", "\n")
    t = t.replace("+ ", "\n- ")

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

    t = t.replace(". ", ".\n\n")
    return t


# -------------------------
# Render principal
# -------------------------
def render():
    st.markdown("## 💼 Vacantes recomendadas para ti")
    st.caption(
        "Estas vacantes se han generado a partir de tu CV, tus skills y, si la has realizado, "
        "la Llamada IA."
    )

    candidate_id = ensure_candidate_id()
    if not candidate_id:
        st.stop()

    with st.spinner("Buscando vacantes con mejor encaje para ti..."):
        jobs = fetch_recommended_jobs(candidate_id)

    if not jobs:
        st.info("No hay vacantes recomendadas por ahora.")
        return

    # --------------------------------
    # Ordenación
    # --------------------------------
    st.markdown("### 🔎 Opciones de visualización")

    sort_option = st.selectbox(
        "Ordenar por",
        ["Mejor encaje global", "Encaje por skills", "Encaje por valores"],
    )

    if sort_option == "Mejor encaje global":
        jobs = sorted(
            jobs,
            key=lambda j: (extract_scores(j).get("global_score") or 0.0),
            reverse=True,
        )
    elif sort_option == "Encaje por skills":
        jobs = sorted(
            jobs,
            key=lambda j: (extract_scores(j).get("skills_match") or 0.0),
            reverse=True,
        )
    elif sort_option == "Encaje por valores":
        jobs = sorted(
            jobs,
            key=lambda j: (extract_scores(j).get("values_match") or 0.0),
            reverse=True,
        )

    # --------------------------------
    # Render de tarjetas
    # --------------------------------
    st.markdown("---")
    st.markdown("### 📋 Lista de vacantes")

    for idx, job in enumerate(jobs):
        job_id = job.get("id") or job.get("job_id")
        title = job.get("title", "Puesto sin título")
        company_name = job.get("company_name") or job.get("company") or "Empresa no indicada"
        location = job.get("location") or "Ubicación no indicada"

        description = job.get("description")
        if description:
            resumen = description[:220] + ("..." if len(description) > 220 else "")
        else:
            resumen = "Sin descripción disponible."

        # 🔥 Scores ya normalizados
        scores = extract_scores(job)

        global_score = scores.get("global_score") or scores.get("global_fit") or 0.0
        skills_score = scores.get("skills_match") or scores.get("skills_fit") or 0.0
        values_score = scores.get("values_match") or scores.get("values_fit") or 0.0
        team_fit_score = scores.get("team_fit") or 0.0

        # 🔑 sufijo único para los keys de Streamlit
        key_suffix = job_id if job_id is not None else f"noid_{idx}"

        # Tarjeta
        with st.container():
            st.markdown("---")
            header_col1, header_col2 = st.columns([3, 1])

            with header_col1:
                st.markdown(f"#### {title}")
                st.caption(f"🏢 {company_name}  ·  📍 {location}")

            with header_col2:
                st.metric("Encaje global", f"{global_score:.0f} / 100")

            st.write(resumen)

            # Subscores
            sub1, sub2, sub3 = st.columns(3)
            with sub1:
                st.progress(min(max(skills_score / 100, 0), 1.0))
                st.caption(f"Encaje en skills: {skills_score:.0f}/100")

            with sub2:
                st.progress(min(max(values_score / 100, 0), 1.0))
                st.caption(f"Encaje en valores: {values_score:.0f}/100")

            with sub3:
                st.progress(min(max(team_fit_score / 100, 0), 1.0))
                st.caption(f"Encaje en equipo: {team_fit_score:.0f}/100")

            # Botones de acción
            action_col1, action_col2 = st.columns([1, 1])

            with action_col1:
                if job_id is not None:
                    if st.button(
                        "🔍 Ver gaps y cómo mejorar para esta vacante",
                        key=f"gaps_{key_suffix}",
                        use_container_width=True,
                    ):
                        st.session_state.selected_job_id = job_id
                        st.session_state.selected_job_title = title
                        st.session_state.current_page = "Mejora (gaps + cursos)"
                        st.rerun()
                else:
                    st.caption("ℹ️ Vacante sin ID interno (no se pueden ver gaps).")

            with action_col2:
                if job_id is not None:
                    if st.button(
                        "✅ Solicitar este puesto",
                        key=f"apply_{key_suffix}",
                        use_container_width=True,
                    ):
                        apply_to_job(job_id, candidate_id)
                else:
                    st.caption("ℹ️ Vacante sin ID interno (no se puede aplicar).")

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
