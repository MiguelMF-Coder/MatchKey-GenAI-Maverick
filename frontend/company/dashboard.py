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
        return None


# -------------------------
# Funciones de ayuda para el dashboard
# -------------------------
def compute_profile_completeness(profile_data: dict) -> int:
    """
    Calcula de forma muy sencilla un % de “completitud” del perfil de empresa,
    solo para dar feedback en el dashboard.
    """
    if not profile_data:
        return 0

    fields = [
        "name",
        "industry",
        "size",
        "location",
        "website",
        "description",
        "values",
        "culture_description",
        "leadership_style",
        "work_mode",
        "team_fit_summary",
    ]

    filled = 0
    total = len(fields)

    for f in fields:
        v = profile_data.get(f)
        if v:
            if isinstance(v, list):
                if len(v) > 0:
                    filled += 1
            else:
                if str(v).strip():
                    filled += 1

    return int((filled / total) * 100)


def extract_values_list(profile_data: dict):
    values = profile_data.get("values") or []
    if isinstance(values, str):
        return [v.strip() for v in values.split(",") if v.strip()]
    if isinstance(values, list):
        return values
    return []


# -------------------------
# Render principal del dashboard
# -------------------------
def render():
    st.markdown("## 📊 Dashboard empresa")
    st.caption(
        "Resumen rápido de tu organización en MatchKey: estado del perfil, valores, cultura "
        "y atajos para gestionar vacantes y talento."
    )

    company_id = ensure_company_id()
    if not company_id:
        st.stop()

    profile_data = fetch_company_profile(company_id) or {}

    name = profile_data.get("name") or "Tu empresa"
    industry = profile_data.get("industry", "Sector no especificado")
    location = profile_data.get("location", "Ubicación no especificada")
    size = profile_data.get("size", "Tamaño no especificado")

    values_list = extract_values_list(profile_data)
    culture_description = profile_data.get("culture_description", "")
    leadership_style = profile_data.get("leadership_style", "")
    work_mode = profile_data.get("work_mode", "No especificado")
    team_fit_summary = profile_data.get("team_fit_summary", "")

    completeness = compute_profile_completeness(profile_data)

    # -------------------------
    # Fila 1: tarjetas resumen
    # -------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🏢 Empresa")
        st.write(f"**Nombre:** {name}")
        st.write(f"**Sector:** {industry}")
        st.write(f"**Ubicación principal:** {location}")
        st.write(f"**Tamaño:** {size}")

        if st.button("Editar perfil de empresa", use_container_width=True):
            st.session_state.current_page = "Perfil empresa"
            st.rerun()

    with col2:
        st.markdown("#### 🌱 Perfil cultural")
        st.write(f"**Valores definidos:** {len(values_list)}")
        if values_list:
            st.caption("Ejemplos: " + ", ".join(values_list[:4]) + ("..." if len(values_list) > 4 else ""))

        st.write(f"**Forma de trabajar:** {work_mode}")

        if completeness < 50:
            st.warning(
                f"Perfil cultural poco completo ({completeness}%). "
                "Te recomendamos rellenar más información en 'Perfil empresa' para mejorar el matching."
            )
        elif completeness < 80:
            st.info(
                f"Perfil cultural en buen camino ({completeness}%). "
                "Puedes afinarlo aún más para mejorar el encaje."
            )
        else:
            st.success(
                f"Perfil cultural muy completo ({completeness}%). "
                "Listo para aprovechar todo el potencial de MatchKey."
            )

    with col3:
        st.markdown("#### 🎯 Próximos pasos recomendados")

        steps = []

        if completeness < 70:
            steps.append("Completar el **Perfil empresa** (valores, cultura, forma de trabajar).")
        steps.append("Crear o revisar al menos una vacante en **Crear vacante**.")
        steps.append("Explorar **Analítica de talento** cuando haya candidatos matcheados.")
        steps.append("Probar el módulo de **Co-Teaching** para vacantes clave.")

        for s in steps:
            st.write(f"- {s}")

    st.markdown("---")

    # -------------------------
    # Fila 2: cultura y encaje ideal
    # -------------------------
    left, right = st.columns([2, 2])

    with left:
        st.markdown("### 🧬 Cómo es vuestra cultura")

        if culture_description:
            st.write(culture_description)
        else:
            st.caption(
                "Todavía no has descrito cómo se viven los valores en el día a día. "
                "Puedes hacerlo en la sección **Perfil empresa**."
            )

        if leadership_style:
            st.markdown("**Estilo de liderazgo predominante:**")
            st.write(leadership_style)
        else:
            st.caption(
                "Añade vuestro estilo de liderazgo en **Perfil empresa** para ayudar a ajustar el encaje de equipo."
            )

    with right:
        st.markdown("### 🧩 Perfil de personas que encajan mejor")

        if team_fit_summary:
            st.write(team_fit_summary)
        else:
            st.caption(
                "Puedes definir qué tipo de personas encajan mejor en vuestra empresa "
                "en el campo '¿Qué tipo de personas encajan mejor?' dentro de **Perfil empresa**."
            )

        st.markdown("---")
        st.markdown("### 🚀 Accesos rápidos")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ Crear vacante", use_container_width=True):
                st.session_state.current_page = "Crear vacante"
                st.rerun()

        with c2:
            if st.button("📈 Analítica de talento", use_container_width=True):
                st.session_state.current_page = "Analítica de talento"
                st.rerun()

        c3, c4 = st.columns(2)
        with c3:
            if st.button("🤝 Co-Teaching", use_container_width=True):
                st.session_state.current_page = "Co-Teaching"
                st.rerun()

        with c4:
            if st.button("🏢 Perfil empresa", use_container_width=True):
                st.session_state.current_page = "Perfil empresa"
                st.rerun()
