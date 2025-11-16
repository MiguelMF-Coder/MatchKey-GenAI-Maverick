import streamlit as st
import requests

BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")


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


def fetch_gaps_for_job(candidate_id, job_id):
    """
    Llama a /candidates/{id}/job/{job}/gaps (GET) para recuperar:
    - skills fuertes
    - skills medias
    - skills a desarrollar
    - recomendaciones (cursos, acciones)

    El contrato puede variar, así que hacemos un parsing defensivo.
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/candidates/{candidate_id}/job/{job_id}/gaps",
            timeout=20,
        )
    except Exception as e:
        st.error(f"Error al obtener los gaps para esta vacante: {e}")
        return None

    if resp.status_code != 200:
        st.error(
            f"No se ha podido obtener la información de gaps (código {resp.status_code})."
        )
        try:
            st.json(resp.json())
        except Exception:
            st.write(resp.text)
        return None

    return resp.json()


# -------------------------
# Render principal de la página
# -------------------------
def render():
    st.markdown("## 📈 Mejora (gaps + cursos)")

    candidate_id = ensure_candidate_id()
    if not candidate_id:
        st.stop()

    job_id = st.session_state.get("selected_job_id")
    job_title = st.session_state.get("selected_job_title", "Vacante seleccionada")

    if not job_id:
        st.info(
            "Primero selecciona una vacante desde la página **'Vacantes recomendadas'** "
            "y pulsa en *'Ver gaps y cómo mejorar para esta vacante'*."
        )
        return

    st.markdown(f"### 🎯 Plan de mejora para: **{job_title}**")

    with st.spinner("Analizando tus gaps y oportunidades de mejora para esta vacante..."):
        gaps_data = fetch_gaps_for_job(candidate_id, job_id)

    if not gaps_data:
        return

    # -------------------------
    # Parsing de datos
    # -------------------------
    # Posibles nombres de campos según backend:
    scores = gaps_data.get("scores") or gaps_data.get("matching") or {}
    global_score = (
        scores.get("global")
        or scores.get("global_score")
        or gaps_data.get("global_score")
    )
    skills_score = (
        scores.get("skills")
        or scores.get("skills_match")
        or gaps_data.get("skills_match")
    )
    values_score = (
        scores.get("values")
        or scores.get("values_match")
        or gaps_data.get("values_match")
    )

    # Info de skills
    skills_section = gaps_data.get("skills") or gaps_data.get("skills_gaps") or {}
    strong_skills = (
        skills_section.get("strong")
        or skills_section.get("high")
        or skills_section.get("good")
        or []
    )
    medium_skills = (
        skills_section.get("medium")
        or skills_section.get("average")
        or skills_section.get("ok")
        or []
    )
    missing_skills = (
        skills_section.get("missing")
        or skills_section.get("to_improve")
        or skills_section.get("weak")
        or []
    )

    recommendations = gaps_data.get("recommendations") or {}
    courses = recommendations.get("courses") or []
    actions = recommendations.get("actions") or recommendations.get("tips") or []

    # -------------------------
    # Resumen de encaje actual
    # -------------------------
    st.markdown("### 📊 Resumen de encaje para esta vacante")

    col1, col2, col3 = st.columns(3)

    with col1:
        if global_score is not None:
            st.metric("Encaje global", f"{global_score:.0f} / 100")
        else:
            st.metric("Encaje global", "N/D")

    with col2:
        if skills_score is not None:
            st.metric("Encaje en skills", f"{skills_score:.0f} / 100")
        else:
            st.metric("Encaje en skills", "N/D")

    with col3:
        if values_score is not None:
            st.metric("Encaje en valores", f"{values_score:.0f} / 100")
        else:
            st.metric("Encaje en valores", "N/D")

    st.markdown("---")

    # -------------------------
    # Skills: fuertes, medias, a desarrollar
    # -------------------------
    st.markdown("### 🧩 Mapa de skills para esta vacante")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("#### ✅ Skills fuertes")
        if strong_skills:
            for s in strong_skills:
                st.write(f"- {s}")
        else:
            st.caption("De momento no se han identificado skills claramente fuertes.")

    with c2:
        st.markdown("#### 🟡 Skills en desarrollo")
        if medium_skills:
            for s in medium_skills:
                st.write(f"- {s}")
        else:
            st.caption("No hay skills intermedias identificadas o no se han devuelto.")

    with c3:
        st.markdown("#### 🔴 Skills a desarrollar")
        if missing_skills:
            for s in missing_skills:
                st.write(f"- {s}")
        else:
            st.caption("No se han identificado gaps claros en skills o el backend no los ha devuelto.")

    st.markdown("---")

    # -------------------------
    # Recomendación de cursos
    # -------------------------
    st.markdown("### 📚 Cursos recomendados para mejorar tu encaje")

    if courses:
        for i, course in enumerate(courses, start=1):
            # Soportamos objetos dict o strings simples
            if isinstance(course, dict):
                title = course.get("title") or course.get("name") or f"Curso {i}"
                provider = course.get("provider") or course.get("platform") or ""
                url = course.get("url") or course.get("link")
                target_skills = course.get("skills") or course.get("target_skills") or []
                level = course.get("level")

                st.markdown(f"**{i}. {title}**")
                if provider or level:
                    extra_bits = []
                    if provider:
                        extra_bits.append(provider)
                    if level:
                        extra_bits.append(level)
                    st.caption(" · ".join(extra_bits))

                if target_skills:
                    if isinstance(target_skills, list):
                        st.caption("Enfocado en: " + ", ".join(target_skills))
                    else:
                        st.caption(f"Enfocado en: {target_skills}")

                if url:
                    st.markdown(f"[Ver curso]({url})")

                st.markdown("---")
            else:
                # Si el backend solo manda textos sueltos
                st.write(f"- {course}")
    else:
        st.info(
            "Todavía no hay cursos recomendados desde el backend para esta vacante. "
            "Próximamente se conectará con el dataset de cursos para proponerte rutas de aprendizaje concretas."
        )

    # -------------------------
    # Otras acciones recomendadas
    # -------------------------
    st.markdown("### 🛠️ Otras acciones sugeridas")

    if actions:
        for a in actions:
            if isinstance(a, dict):
                text = a.get("text") or a.get("description")
                if text:
                    st.write(f"- {text}")
            else:
                st.write(f"- {a}")
    else:
        st.caption(
            "El backend no ha devuelto acciones adicionales específicas. "
            "Aun así, centrarte en las skills en rojo y amarillo ya mejorará mucho tu encaje."
        )
