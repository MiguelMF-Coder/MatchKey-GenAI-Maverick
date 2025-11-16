import streamlit as st
import requests

BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")


# -------------------------
# Helpers de backend
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
    Llama a /companies/{id}/profile (GET) para recuperar los datos actuales.
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
            f"No se ha podido cargar el perfil de empresa (código {resp.status_code}). "
            "Puede que aún no esté creado o esté vacío."
        )
        return None


def update_company_profile(company_id, profile_data):
    """
    Envía los datos de perfil al backend.
    Suponemos que el backend acepta PUT en /companies/{id}/profile con JSON.
    Ajusta a PATCH/POST si tu API lo requiere.
    """
    try:
        resp = requests.put(
            f"{BACKEND_URL}/companies/{company_id}/profile",
            json=profile_data,
            timeout=10,
        )
    except Exception as e:
        st.error(f"Error al actualizar el perfil de empresa: {e}")
        return False

    if resp.status_code in (200, 201):
        st.success("Perfil de empresa actualizado correctamente ✅")
        return True
    else:
        st.error(
            f"No se ha podido actualizar el perfil de empresa. Código: {resp.status_code}"
        )
        return False


# -------------------------
# Render principal de la página
# -------------------------
def render():
    st.markdown("## 🏢 Perfil de la empresa")
    st.caption(
        "Define quién eres, cómo trabajáis y qué valores os representan. "
        "Esta información se utilizará para el encaje cultural y de equipo con los candidatos."
    )

    company_id = ensure_company_id()
    if not company_id:
        st.stop()

    # Cargar perfil actual desde el backend (si existe)
    profile_data = fetch_company_profile(company_id) or {}

    # Valores iniciales (si no hay nada, ponemos cosas vacías)
    name_init = profile_data.get("name", "")
    industry_init = profile_data.get("industry", "")
    size_init = profile_data.get("size", "")
    location_init = profile_data.get("location", "")
    website_init = profile_data.get("website", "")
    description_init = profile_data.get("description", "")

    # Bloque de valores/cultura
    values_init = profile_data.get("values", [])
    culture_init = profile_data.get("culture_description", "")
    leadership_style_init = profile_data.get("leadership_style", "")
    work_mode_init = profile_data.get("work_mode", "")
    perks_init = profile_data.get("perks", "")
    team_fit_summary_init = profile_data.get("team_fit_summary", "")

    # Layout de la página
    col_left, col_right = st.columns([2, 2])

    # -------------------------
    # Columna izquierda: Datos básicos
    # -------------------------
    with col_left:
        st.markdown("### 📝 Datos básicos de la empresa")

        with st.form("company_basic_profile_form"):
            name = st.text_input("Nombre de la empresa", value=name_init)
            industry = st.text_input(
                "Sector / industria",
                value=industry_init,
                placeholder="Ej. Consultoría tecnológica, E-commerce, Banca, SaaS...",
            )
            size = st.text_input(
                "Tamaño aproximado (nº empleados)",
                value=size_init,
                placeholder="Ej. 11–50, 51–200, 200–500...",
            )
            location = st.text_input(
                "Ubicación principal",
                value=location_init,
                placeholder="Ciudad, País",
            )
            website = st.text_input(
                "Sitio web",
                value=website_init,
                placeholder="https://tuempresa.com",
            )
            description = st.text_area(
                "Descripción de la empresa",
                value=description_init,
                height=150,
                placeholder="Explica brevemente quiénes sois, qué hacéis y cuál es vuestro propósito.",
            )

            submitted_basic = st.form_submit_button("Guardar datos básicos")

        if submitted_basic:
            if not name:
                st.error("El nombre de la empresa es obligatorio.")
            else:
                payload = {
                    "name": name,
                    "industry": industry,
                    "size": size,
                    "location": location,
                    "website": website,
                    "description": description,
                }
                # Merge con datos existentes para no pisar valores/cultura
                payload.update(
                    {
                        "values": profile_data.get("values", values_init),
                        "culture_description": profile_data.get(
                            "culture_description", culture_init
                        ),
                        "leadership_style": profile_data.get(
                            "leadership_style", leadership_style_init
                        ),
                        "work_mode": profile_data.get(
                            "work_mode", work_mode_init
                        ),
                        "perks": profile_data.get("perks", perks_init),
                        "team_fit_summary": profile_data.get(
                            "team_fit_summary", team_fit_summary_init
                        ),
                    }
                )
                update_company_profile(company_id, payload)

    # -------------------------
    # Columna derecha: Valores, cultura y forma de trabajar
    # -------------------------
    with col_right:
        st.markdown("### 🌱 Valores y cultura")

        # Valores: multiselect sencillo
        possible_values = [
            "Transparencia",
            "Innovación",
            "Trabajo en equipo",
            "Orientación a resultados",
            "Orientación a las personas",
            "Impacto social",
            "Aprendizaje continuo",
            "Autonomía",
            "Estabilidad",
            "Diversidad & Inclusión",
        ]

        # Normalizamos a lista
        values_init_list = (
            values_init
            if isinstance(values_init, list)
            else (values_init.split(",") if isinstance(values_init, str) else [])
        )

        with st.form("company_culture_form"):
            selected_values = st.multiselect(
                "Valores que mejor describen a vuestra empresa",
                options=possible_values,
                default=[v for v in values_init_list if v in possible_values],
                help="Estos valores se utilizarán para el encaje cultural con los candidatos.",
            )

            culture_description = st.text_area(
                "¿Cómo se viven estos valores en el día a día?",
                value=culture_init,
                height=120,
                placeholder="Ej. Cómo tomáis decisiones, cómo dais feedback, cómo celebráis los logros...",
            )

            leadership_style = st.text_area(
                "Estilo de liderazgo predominante",
                value=leadership_style_init,
                height=100,
                placeholder="Ej. Liderazgo cercano, muy orientado a resultados, mucha autonomía, etc.",
            )

            work_mode = st.selectbox(
                "Forma de trabajar",
                [
                    "No especificado",
                    "Principalmente remoto",
                    "Híbrido",
                    "Principalmente presencial",
                ],
                index=(
                    ["No especificado", "Principalmente remoto", "Híbrido", "Principalmente presencial"]
                    .index(work_mode_init)
                    if work_mode_init in [
                        "No especificado",
                        "Principalmente remoto",
                        "Híbrido",
                        "Principalmente presencial",
                    ]
                    else 0
                ),
            )

            perks = st.text_area(
                "Beneficios / perks destacados",
                value=perks_init,
                height=100,
                placeholder="Ej. Formación, seguro médico, días de teletrabajo, presupuesto para conferencias...",
            )

            team_fit_summary = st.text_area(
                "¿Qué tipo de personas encajan mejor en vuestra empresa?",
                value=team_fit_summary_init,
                height=120,
                placeholder="Ej. Personas autónomas que disfrutan del cambio, con ganas de aprender y que valoren el trabajo en equipo.",
            )

            submitted_culture = st.form_submit_button("Guardar valores y cultura")

        if submitted_culture:
            payload = {
                "name": profile_data.get("name", name_init),
                "industry": profile_data.get("industry", industry_init),
                "size": profile_data.get("size", size_init),
                "location": profile_data.get("location", location_init),
                "website": profile_data.get("website", website_init),
                "description": profile_data.get("description", description_init),
                "values": selected_values,
                "culture_description": culture_description,
                "leadership_style": leadership_style,
                "work_mode": work_mode,
                "perks": perks,
                "team_fit_summary": team_fit_summary,
            }
            update_company_profile(company_id, payload)

        st.markdown("---")

        st.markdown("### 🔍 Cómo se usará esta información")
        st.caption(
            "Estos datos se utilizarán para calcular el encaje cultural y de equipo con los candidatos "
            "(valores detectados y preferencias de equipo provenientes de la Llamada IA)."
        )

        if st.button("Ir a crear vacante", use_container_width=True):
            st.session_state.current_page = "Crear vacante"
            st.experimental_rerun()
