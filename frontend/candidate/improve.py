import streamlit as st
import requests
from utils import get_backend_url, api_get

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


def fetch_gaps_for_job(candidate_id, job_id):
    """
    Llama a /candidates/{id}/job/{job}/gaps (GET) para recuperar:
    - skills fuertes
    - skills medias
    - skills a desarrollar
    - recomendaciones (acciones)

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


def fetch_recommended_courses_for_job(candidate_id: int, job_id: int):
    """
    Llama al endpoint /candidates/{candidate_id}/job/{job_id}/recommended_courses
    y devuelve (data, error).
    """
    path = f"/candidates/{candidate_id}/job/{job_id}/recommended_courses"
    data, err = api_get(path)

    if err:
        return None, err

    return data, None


def show_courses_catalog():
    st.subheader("📚 Cursos disponibles")

    courses, err = api_get("/candidates/courses")

    if err:
        st.error("No se pudieron cargar los cursos de mejora.")
        return

    if not courses:
        st.info("De momento no hay cursos disponibles en el catálogo.")
        return

    # Opciones de filtro simples
    categories = sorted({c.get("category", "Sin categoría") for c in courses})
    selected_category = st.selectbox("Filtrar por categoría", ["Todas"] + categories)

    search_term = st.text_input("Buscar por nombre o skill asociada")

    # Filtrado en memoria
    filtered = []
    for c in courses:
        name = c.get("name", "")
        skills_str = c.get("skills", "") or ""
        category = c.get("category", "Sin categoría")

        if selected_category != "Todas" and category != selected_category:
            continue

        if search_term:
            term = search_term.lower()
            if term not in name.lower() and term not in skills_str.lower():
                continue

        filtered.append(c)

    st.markdown(f"Mostrando **{len(filtered)}** cursos")

    # Render de tarjetas de curso
    for course in filtered:
        name = course.get("name", "Curso sin nombre")
        url = course.get("url", "#")
        category = course.get("category", "Sin categoría")
        language = course.get("language", "N/A")
        skills_str = course.get("skills", "")
        what_you_learn = course.get("what_you_learn", "")
        content = course.get("content", "")

        with st.container(border=True):
            st.markdown(f"### {name}")
            st.markdown(f"**Categoría:** {category} · **Idioma:** {language}")

            if skills_str:
                st.markdown(f"**Skills relacionadas:** {skills_str}")

            if what_you_learn:
                st.markdown(f"**Qué aprenderás:** {what_you_learn}")
            else:
                # Si no tenemos what_you_learn, usamos un trocito del content
                if content:
                    snippet = content[:260] + "..." if len(content) > 260 else content
                    st.markdown(snippet)

            if url and url != "#":
                st.markdown(f"[🔗 Ir al curso]({url})")


def show_recommended_courses_section(reco_data: dict):
    """
    Renderiza la sección de cursos recomendados para la vacante concreta.
    Espera el JSON devuelto por /recommended_courses.
    """
    st.subheader("🎓 Cursos recomendados para esta vacante")

    missing_skills = reco_data.get("missing_skills", []) or []
    courses = reco_data.get("courses", []) or []

    if missing_skills:
        skills_str = ", ".join(missing_skills)
        st.markdown(f"Estas recomendaciones están basadas en tus gaps: **{skills_str}**")
    else:
        st.markdown("No se han detectado skills en las que tengas gaps para esta vacante.")

    if not courses:
        st.info("Por ahora no hemos encontrado cursos relevantes para tus gaps en esta vacante.")
        return

    st.markdown(f"Encontramos **{len(courses)}** cursos que pueden ayudarte:")

    for course in courses:
        title = course.get("title", "Curso sin nombre")
        provider = course.get("provider", None)
        url = course.get("url", "#")
        target_skills = course.get("target_skills", []) or []

        with st.container(border=True):
            st.markdown(f"### {title}")

            if provider:
                st.markdown(f"**Categoría / proveedor:** {provider}")

            if target_skills:
                st.markdown(
                    "✅ Este curso te ayuda con: " +
                    ", ".join(f"`{s}`" for s in target_skills)
                )

            if url and url != "#":
                st.markdown(f"[🔗 Ver curso recomendado]({url})")


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

    # 1) Gaps para esta vacante
    with st.spinner("Analizando tus gaps y oportunidades de mejora para esta vacante..."):
        gaps_data = fetch_gaps_for_job(candidate_id, job_id)

    if not gaps_data:
        return

    # -------------------------
    # Parsing de datos
    # -------------------------
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
    # Mapa de skills
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

    # -------------------------
    # Cursos recomendados (motor nuevo) + catálogo general
    # -------------------------
    st.markdown("---")
    with st.spinner("Buscando cursos recomendados para tus gaps en esta vacante..."):
        reco_data, reco_err = fetch_recommended_courses_for_job(candidate_id, job_id)

    if reco_err:
        st.error("No se pudieron obtener cursos recomendados para esta vacante.")
    elif reco_data:
        show_recommended_courses_section(reco_data)

    st.markdown("---")
    show_courses_catalog()
