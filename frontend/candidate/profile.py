import streamlit as st
import requests
from utils import get_backend_url

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
        st.warning(
            f"No se ha podido cargar tu perfil todavía (código {resp.status_code}). "
            "Puede que aún no esté creado o esté vacío."
        )
        return None


def update_candidate_profile(candidate_id, profile_data):
    """
    Envía los datos de perfil (sin CV) al backend.
    Suponemos que el backend acepta PUT en /candidates/{id}/profile con JSON.
    Ajusta a PATCH/POST si tu API lo requiere.
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


def upload_cv_and_parse(candidate_id, uploaded_file):
    """
    Envía el CV al backend para que lo procese (Document Parser + Skills Extractor).
    Aquí asumimos un endpoint tipo:
      POST /candidates/{id}/profile?parse_cv=true
    con multipart/form-data (file=...).
    Ajusta la URL o el nombre del campo según tu backend real.
    """
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}

    try:
        resp = requests.post(
            f"{BACKEND_URL}/candidates/{candidate_id}/profile",
            params={"parse_cv": "true"},
            files=files,
            timeout=60,
        )
    except Exception as e:
        st.error(f"Error al subir y procesar el CV: {e}")
        return None

    if resp.status_code not in (200, 201):
        st.error(f"No se ha podido procesar el CV. Código: {resp.status_code}")
        return None

    return resp.json()


# -------------------------
# Render principal de la página
# -------------------------
def render():
    st.markdown("## 👤 Mi perfil")

    # Aseguramos que el usuario logado es un candidato registrado en el backend
    candidate_id = ensure_candidate_id()
    if not candidate_id:
        st.stop()

    # Cargar perfil actual desde el backend (si existe)
    profile_data = fetch_candidate_profile(candidate_id) or {}

    # Valores iniciales (si no hay nada, ponemos cosas vacías)
    name_init = profile_data.get("name", "")
    headline_init = profile_data.get("headline", "")
    location_init = profile_data.get("location", "")
    summary_init = profile_data.get("summary", "")

    # Layout de la página
    col_left, col_right = st.columns([2, 2])

    # -------------------------
    # Columna izquierda: Datos básicos
    # -------------------------
    with col_left:
        st.markdown("### 📝 Datos básicos")

        with st.form("basic_profile_form"):
            name = st.text_input("Nombre completo", value=name_init)
            headline = st.text_input(
                "Titular profesional",
                value=headline_init,
                placeholder="Ej. Data Analyst especializado en BI y visualización",
            )
            location = st.text_input(
                "Ubicación",
                value=location_init,
                placeholder="Ciudad, País",
            )
            summary = st.text_area(
                "Resumen / Sobre mí",
                value=summary_init,
                height=150,
                placeholder="Cuéntanos brevemente quién eres, tu experiencia y qué buscas.",
            )

            submitted = st.form_submit_button("Guardar perfil")

        if submitted:
            if not name:
                st.error("El nombre completo es obligatorio.")
            else:
                payload = {
                    "name": name,
                    "headline": headline,
                    "location": location,
                    "summary": summary,
                }
                update_candidate_profile(candidate_id, payload)

        # Si el backend devuelve skills en el perfil, los mostramos como referencia rápida
        existing_skills = profile_data.get("skills") or profile_data.get("all_skills")
        if existing_skills:
            st.markdown("#### 🧩 Skills detectados en tu perfil")
            st.caption("Estos pueden venir de tu CV o de entrevistas previas.")
            st.write(", ".join(existing_skills))

    # -------------------------
    # Columna derecha: CV + Llamada IA
    # -------------------------
    with col_right:
        # Bloque CV
        st.markdown("### 📄 CV y análisis con IA")
        st.caption(
            "Sube tu CV en PDF, DOCX o imagen. El sistema lo analizará con OCR y "
            "extraerá tus skills automáticamente."
        )

        uploaded_file = st.file_uploader(
            "Subir CV",
            type=["pdf", "docx", "doc", "png", "jpg", "jpeg"],
        )

        if uploaded_file is not None:
            if st.button("Procesar CV con IA"):
                with st.spinner("Analizando tu CV..."):
                    analysis_result = upload_cv_and_parse(candidate_id, uploaded_file)

                if analysis_result:
                    st.success("CV analizado correctamente ✅")

                    # Mostramos algunos campos típicos devueltos por el backend
                    raw_text = analysis_result.get("raw_text")
                    clean_text = analysis_result.get("clean_text")
                    must_have = analysis_result.get("must_have") or analysis_result.get("must_skills")
                    nice_to_have = analysis_result.get("nice_to_have")
                    all_skills = analysis_result.get("all_skills")

                    if all_skills:
                        st.markdown("#### 🧩 Skills detectados")
                        st.write(", ".join(all_skills))

                    col1, col2 = st.columns(2)
                    with col1:
                        if must_have:
                            st.markdown("##### ✅ Skills fuertes (Must-have)")
                            st.write(", ".join(must_have))
                    with col2:
                        if nice_to_have:
                            st.markdown("##### ⭐ Skills adicionales (Nice-to-have)")
                            st.write(", ".join(nice_to_have))

                    with st.expander("Ver texto parseado del CV"):
                        if clean_text:
                            st.markdown("##### Texto limpio")
                            st.write(clean_text[:5000])  # por si es muy largo
                        elif raw_text:
                            st.markdown("##### Texto bruto")
                            st.write(raw_text[:5000])
                        else:
                            st.info("El backend no ha devuelto texto parseado del CV.")

        # Si el perfil ya tenía información de análisis previa, la mostramos abajo
        if profile_data.get("analysis"):
            st.markdown("### 📊 Último análisis guardado")
            st.json(profile_data["analysis"])

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
