import streamlit as st
import requests

from utils import (
    get_backend_url,
    api_post_file,
    require_role,
)

BACKEND_URL = get_backend_url()

# -------------------------
# Helpers de backend
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
        resp = requests.post(f"{BACKEND_URL}/candidates/create", json=payload, timeout=10)
    except Exception as e:
        st.error(f"Error al crear el candidato en el backend: {e}")
        return None

    if resp.status_code not in (200, 201):
        st.error(f"No se ha podido registrar el candidato. Código: {resp.status_code}")
        return None

    data = resp.json()
    candidate_id = data.get("id") or data.get("candidate_id")

    if not candidate_id:
        st.error("El backend no devolvió un candidate_id válido.")
        return None

    st.session_state.candidate_id = candidate_id
    return candidate_id


def fetch_candidate_profile(candidate_id: int):
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
        st.warning(
            f"No se ha podido cargar tu perfil todavía (código {resp.status_code}). "
            "Puede que aún no esté creado o esté vacío."
        )
        return None


def update_candidate_profile(candidate_id: int, profile_data: dict):
    """
    Envía los datos de perfil al backend.
    Suponemos que el backend acepta PUT en /candidates/{id}/profile con JSON.
    """
    try:
        resp = requests.put(
            f"{BACKEND_URL}/candidates/{candidate_id}/profile",
            json=profile_data,
            timeout=10,
        )
    except Exception as e:
        st.error(f"Error al actualizar el perfil: {e}")
        return False

    if resp.status_code in (200, 201):
        st.success("Perfil actualizado correctamente ✅")
        return True
    else:
        st.error(f"No se ha podido actualizar el perfil. Código: {resp.status_code}")
        return False


def upload_cv_and_parse(candidate_id: int, uploaded_file):
    """
    Llama al endpoint /candidates/{id}/parse_cv con el fichero subido
    y devuelve la respuesta del backend ya en dict.

    Respuesta esperada:
    {
      "status": "success",
      "candidate_id": ...,
      "updated_candidate": {...},
      "skills_detected": [...],
      "parsed_cv": {...}
    }
    """
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/octet-stream",
        )
    }

    from utils import api_post_file  # import local para evitar problemas circulares
    data, error = api_post_file(f"/candidates/{candidate_id}/parse_cv", files=files)

    if error:
        st.error(f"Error procesando CV: {error}")
        return None

    return data


# -------------------------
# Render principal de la página
# -------------------------
def render():
    require_role("candidate")
    st.markdown("## 👤 Mi perfil")

        # Estilos para las pills de skills
    st.markdown(
        """
        <style>
        .skill-pill {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.35rem 0.9rem;
            margin: 0.25rem;
            border-radius: 999px;
            background: rgba(161, 0, 255, 0.22);
            border: 1px solid rgba(255, 255, 255, 0.18);
            min-width: 110px;
            text-align: center;
            font-size: 0.85rem;
            font-weight: 500;
            color: #FFFFFF;            /* texto más visible */
            white-space: nowrap;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Aseguramos que el usuario logado es un candidato registrado en el backend
    candidate_id = ensure_candidate_id()
    if not candidate_id:
        st.stop()

    # Cargar perfil actual desde el backend (si existe)
    profile_data = fetch_candidate_profile(candidate_id) or {}

    # Último análisis de CV guardado en sesión o en el propio perfil (si el backend lo guarda allí)
    last_analysis = st.session_state.get("last_cv_analysis")
    if not last_analysis and profile_data.get("analysis"):
        last_analysis = {
            "parsed_cv": profile_data["analysis"],
            "updated_candidate": {},
            "skills_detected": profile_data.get("all_skills") or profile_data.get("skills") or [],
        }

    # -------------------------
    # 1. Bloque: subir CV y analizar
    # -------------------------
    st.markdown("### 📄 CV y análisis automático")
    st.caption(
        "Sube tu CV en PDF, DOCX o imagen. El sistema lo analizará con OCR, "
        "actualizará tu perfil y guardará tus skills."
    )

    uploaded_file = st.file_uploader(
        "Subir CV",
        type=["pdf", "docx", "doc", "png", "jpg", "jpeg"],
    )

    if uploaded_file is not None:
        if st.button("Procesar CV y actualizar perfil"):
            with st.spinner("Analizando tu CV, extrayendo información y actualizando tu perfil..."):
                analysis_result = upload_cv_and_parse(candidate_id, uploaded_file)

            if analysis_result:
                st.success("CV analizado y perfil actualizado correctamente ✅")
                st.session_state.last_cv_analysis = analysis_result
                last_analysis = analysis_result

    st.markdown("---")

    # -------------------------
    # 2. Formulario principal editable (basado en perfil + CV)
    # -------------------------
    parsed_cv = (last_analysis or {}).get("parsed_cv", {}) or {}
    updated_from_cv = (last_analysis or {}).get("updated_candidate", {}) or {}

    # Datos sugeridos desde CV
    nombre_cv = updated_from_cv.get("first_name") or parsed_cv.get("Nombre", "")
    apellidos_cv = updated_from_cv.get("last_name") or parsed_cv.get("Apellidos", "")
    full_name_cv = (
        updated_from_cv.get("full_name")
        or " ".join([p for p in [nombre_cv, apellidos_cv] if p]).strip()
    )

    ubicacion_cv = updated_from_cv.get("location") or parsed_cv.get("Ubicacion", "")

    contacto_cv = parsed_cv.get("Contacto", {}) or {}
    email_cv = updated_from_cv.get("contact_email") or contacto_cv.get("Email", "")
    phone_cv = updated_from_cv.get("contact_phone") or contacto_cv.get("Telefono", "")

    # Valores iniciales finales (prioridad: perfil guardado > CV)
    name_init = profile_data.get("name") or full_name_cv
    location_init = profile_data.get("location") or ubicacion_cv
    headline_init = profile_data.get("headline") or ""
    summary_init = profile_data.get("summary") or ""
    email_init = profile_data.get("contact_email") or email_cv
    phone_init = profile_data.get("contact_phone") or phone_cv

    st.markdown("### 📝 Datos de tu perfil (editables)")
    st.caption("Estos datos se basan en tu CV y en la información ya guardada en tu perfil. Puedes ajustarlos a mano.")

    with st.form("profile_from_cv_form"):
        name = st.text_input("Nombre completo", value=name_init or "")
        location = st.text_input("Ubicación", value=location_init or "", placeholder="Ciudad, País")
        email = st.text_input("Email de contacto", value=email_init or "")
        phone = st.text_input("Teléfono de contacto", value=phone_init or "")
        headline = st.text_input(
            "Titular profesional",
            value=headline_init or "",
            placeholder="Ej. Data Analyst especializado en BI y visualización",
        )
        summary = st.text_area(
            "Resumen / Sobre mí",
            value=summary_init or "",
            height=150,
            placeholder="Cuéntanos brevemente quién eres, tu experiencia y qué buscas.",
        )

        save_submitted = st.form_submit_button("Guardar perfil")

    if save_submitted:
        if not name:
            st.error("El nombre completo es obligatorio.")
        else:
            payload = {
                "name": name,
                "headline": headline,
                "location": location,
                "summary": summary,
                # estos campos puede que el backend ya los soporte; si no, los ignorará
                "contact_email": email,
                "contact_phone": phone,
            }
            if update_candidate_profile(candidate_id, payload):
                profile_data.update(payload)

    # Skills actuales en perfil (o detectadas)
    existing_skills = (
        profile_data.get("skills")
        or profile_data.get("all_skills")
        or (last_analysis or {}).get("skills_detected")
        or (parsed_cv.get("Skills") if parsed_cv else [])
    )

    if existing_skills:
        cols = st.columns(4)
        for i, sk in enumerate(existing_skills):
            with cols[i % 4]:
                st.markdown(
                    f'<div class="skill-pill">{sk}</div>',
                    unsafe_allow_html=True,
                )
    else:
        st.caption("Todavía no hay skills detectadas. Sube tu CV para extraerlas automáticamente.")


    st.markdown("---")

    # -------------------------
    # 3. Tabs con detalle del CV analizado
    # -------------------------
    if parsed_cv:
        st.markdown("### 📑 Resumen del CV analizado")

        tabs = st.tabs(
            [
                "Datos personales",
                "Formación",
                "Experiencia",
                "Idiomas & skills",
                "Texto extraído",
            ]
        )

        # TAB 1: Datos personales
        with tabs[0]:
            st.markdown("#### 🙋 Datos personales detectados")

            fecha_ini = parsed_cv.get("Fecha_inicio", "")
            fecha_fin = parsed_cv.get("Fecha_finalizacion", "")

            st.write(f"**Nombre completo (desde CV):** {full_name_cv or '—'}")
            st.write(f"**Ubicación (desde CV):** {ubicacion_cv or '—'}")
            st.write(f"**Email (desde CV):** {email_cv or '—'}")
            st.write(f"**Teléfono (desde CV):** {phone_cv or '—'}")

            if fecha_ini or fecha_fin:
                st.write(f"**Rango de fechas detectado en el CV:** {fecha_ini} - {fecha_fin}")

        # TAB 2: Formación
        with tabs[1]:
            st.markdown("#### 🎓 Formación detectada")
            estudios = parsed_cv.get("Estudios", "")
            if estudios:
                for linea in estudios.split("\n"):
                    linea = linea.strip()
                    if linea:
                        st.markdown(f"- {linea}")
            else:
                st.info("No se ha detectado sección de estudios en el CV.")

        # TAB 3: Experiencia
        with tabs[2]:
            st.markdown("#### 💼 Experiencia profesional")
            experiencia = parsed_cv.get("Experiencia", {}) or {}

            empleos = experiencia.get("Empleos") or []
            practicas = experiencia.get("Practicas") or []
            proyectos = experiencia.get("Proyectos") or []

            if not (empleos or practicas or proyectos):
                st.info("No se ha podido estructurar la experiencia a partir del CV.")
            else:
                if empleos:
                    st.markdown("##### 🧱 Empleos")
                    for block in empleos:
                        st.markdown(f"- {block}")

                if practicas:
                    st.markdown("##### 🎓 Prácticas / Becas")
                    for block in practicas:
                        st.markdown(f"- {block}")

                if proyectos:
                    st.markdown("##### 🧪 Proyectos")
                    for block in proyectos:
                        st.markdown(f"- {block}")

        # TAB 4: Idiomas & skills
        with tabs[3]:
            st.markdown("#### 🌍 Idiomas")
            idiomas = parsed_cv.get("Idiomas", []) or []
            if idiomas:
                st.write(", ".join(idiomas))
            else:
                st.info("No se han detectado idiomas en el CV.")

            st.markdown("#### 🧠 Skills detectadas en el CV")
            skills_from_parser = parsed_cv.get("Skills", []) or []
            all_cv_skills = (last_analysis or {}).get("skills_detected") or skills_from_parser

            if all_cv_skills:
                cols = st.columns(4)
                for i, sk in enumerate(all_cv_skills):
                    with cols[i % 4]:
                        st.markdown(
                            f'<div class="skill-pill">{sk}</div>',
                            unsafe_allow_html=True,
                        )
            else:
                st.info("No se han detectado skills en el CV.")

        # TAB 5: Texto extraído
        with tabs[4]:
            st.markdown("#### 📄 Texto extraído del CV")
            raw_preview = parsed_cv.get("raw_text_preview", "")
            if raw_preview:
                st.code(raw_preview, language="markdown")
            else:
                st.info("No se pudo extraer texto del CV o el texto disponible es demasiado corto.")

    st.markdown("---")

    # Bloque Llamada IA
    st.markdown("### 🔮 Completa tu perfil con la Llamada IA")
    st.caption(
        "Si quieres que el sistema detecte tus motivaciones, valores, soft skills y preferencias "
        "de equipo, puedes completar tu perfil a través de la Llamada IA."
    )

    if st.button("✨ Completar perfil con Llamada IA", use_container_width=True):
        st.session_state.current_page = "Llamada IA"
        st.rerun()
