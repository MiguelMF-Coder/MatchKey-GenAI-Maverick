import streamlit as st
from utils import apply_accenture_theme
from utils import get_backend_url

# --------- IMPORTS DE PÁGINAS POR ROL ---------
# CANDIDATO
from candidate import dashboard as candidate_dashboard
from candidate import profile as candidate_profile
from candidate import call_ai as candidate_call_ai
from candidate import jobs as candidate_jobs
from candidate import improve as candidate_improve

# EMPRESA
from company import dashboard as company_dashboard
from company import profile as company_profile
from company import create_job as company_create_job
from company import analytics as company_analytics
from company import co_teaching as company_co_teaching


BACKEND_URL = get_backend_url()

# -------------------------
# Inicialización de sesión
# -------------------------
def init_session_state():
    if "auth" not in st.session_state:
        st.session_state.auth = {
            "is_authenticated": False,
            "user_id": None,
            "email": None,
        }
    if "role" not in st.session_state:
        st.session_state.role = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Inicio"


# -------------------------
# UI Pública (Landing)
# -------------------------
def render_public_landing():
    st.markdown("### 🔑 Bienvenido a MatchKey")
    st.markdown(
        """
MatchKey es un portal de empleo inteligente que conecta **personas** y **empresas** 
no solo por skills, sino también por **valores**, **cultura** y **encaje de equipo**.
"""
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 👤 Soy Candidato")
        st.markdown(
            """
- Sube tu **CV** una sola vez  
- Deja que la IA detecte tus **skills**  
- Descubre vacantes **alineadas contigo**  
- Identifica **gaps** y recibe recomendaciones de **cursos**  
"""
        )

    with col2:
        st.markdown("#### 🏢 Soy Empresa")
        st.markdown(
            """
- Define tu **cultura** y **valores**  
- Sube las **vacantes** (PDF / JD)  
- Deja que el motor de matching puntúe candidatos  
- Explora **Co-Teaching** y analíticas de talento  
"""
        )

    st.markdown("---")


# -------------------------
# Formulario de Login (simplificado)
# -------------------------
def render_login_card():
    st.subheader("Inicia sesión para acceder a tu portal")

    with st.form("login_form", clear_on_submit=False):
        role_choice = st.radio(
            "¿Cómo quieres entrar?",
            ["👤 Candidato", "🏢 Empresa"],
            horizontal=True,
        )

        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")

        submitted = st.form_submit_button("Entrar")

    if submitted:
        if not email or not password:
            st.error("Por favor, introduce email y contraseña.")
            return

        # 🔐 Aquí en el futuro se integrará con el backend de auth
        role = "candidate" if "Candidato" in role_choice else "company"

        st.session_state.auth["is_authenticated"] = True
        st.session_state.auth["user_id"] = email  # temporal
        st.session_state.auth["email"] = email
        st.session_state.role = role
        st.session_state.current_page = "Inicio"

        st.success("Inicio de sesión correcto. Cargando tu portal...")


# -------------------------
# Header privado (cuando ya hay sesión)
# -------------------------
def render_private_header():
    role = st.session_state.role
    email = st.session_state.auth.get("email")

    left, right = st.columns([3, 1])

    with left:
        if role == "candidate":
            st.markdown("### 👤 Portal Candidato")
        elif role == "company":
            st.markdown("### 🏢 Portal Empresa")

        if email:
            st.caption(f"Conectado como: **{email}**")

    with right:
        if st.button("Cerrar sesión"):
            # Reset de sesión
            st.session_state.auth = {
                "is_authenticated": False,
                "user_id": None,
                "email": None,
            }
            st.session_state.role = None
            st.session_state.current_page = "Inicio"
            st.rerun()


# -------------------------
# Menú lateral por rol
# -------------------------
def render_sidebar_navigation():
    role = st.session_state.role

    with st.sidebar:
        st.markdown("## 🧭 Navegación")
        if role == "candidate":
            page = st.radio(
                "Secciones",
                [
                    "Inicio",
                    "Mi perfil",
                    "Llamada IA",
                    "Vacantes recomendadas",
                    "Mejora (gaps + cursos)",
                    "Dashboard",  # 👈 Dashboard como página aparte
                ],
                index=[
                    "Inicio",
                    "Mi perfil",
                    "Llamada IA",
                    "Vacantes recomendadas",
                    "Mejora (gaps + cursos)",
                    "Dashboard",
                ].index(st.session_state.current_page)
                if st.session_state.current_page in [
                    "Inicio",
                    "Mi perfil",
                    "Llamada IA",
                    "Vacantes recomendadas",
                    "Mejora (gaps + cursos)",
                    "Dashboard",
                ]
                else 0,
            )
        else:  # company
            page = st.radio(
                "Secciones",
                [
                    "Inicio",
                    "Perfil empresa",
                    "Crear vacante",
                    "Analítica de talento",
                    "Co-Teaching",
                    "Dashboard",  # 👈 Dashboard como página aparte
                ],
                index=[
                    "Inicio",
                    "Perfil empresa",
                    "Crear vacante",
                    "Analítica de talento",
                    "Co-Teaching",
                    "Dashboard",
                ].index(st.session_state.current_page)
                if st.session_state.current_page in [
                    "Inicio",
                    "Perfil empresa",
                    "Crear vacante",
                    "Analítica de talento",
                    "Co-Teaching",
                    "Dashboard",
                ]
                else 0,
            )

        st.session_state.current_page = page


# -------------------------
# Contenido de cada portal
# -------------------------
def render_candidate_portal():
    page = st.session_state.current_page

    if page == "Inicio":
        st.markdown("#### 👋 Bienvenido/a a tu espacio MatchKey")
        st.write(
            "Desde el menú lateral puedes subir tu CV, hablar con la IA, ver vacantes recomendadas, "
            "trabajar en tus gaps o consultar tu dashboard cuando necesites información agregada."
        )

    elif page == "Mi perfil":
        candidate_profile.render()

    elif page == "Llamada IA":
        candidate_call_ai.render()

    elif page == "Vacantes recomendadas":
        candidate_jobs.render()

    elif page == "Mejora (gaps + cursos)":
        candidate_improve.render()

    elif page == "Dashboard":
        # 👇 SOLO aquí entramos al dashboard del candidato
        candidate_dashboard.render()

    else:
        st.error("Página no encontrada para candidato.")


def render_company_portal():
    page = st.session_state.current_page

    if page == "Inicio":
        st.markdown("#### 👋 Bienvenido/a al portal empresa de MatchKey")
        st.write(
            "Desde el menú lateral puedes definir tu perfil, crear vacantes, ver analíticas "
            "y acceder al dashboard cuando necesites una visión global."
        )

    elif page == "Perfil empresa":
        company_profile.render()

    elif page == "Crear vacante":
        company_create_job.render()

    elif page == "Analítica de talento":
        company_analytics.render()

    elif page == "Co-Teaching":
        company_co_teaching.render()

    elif page == "Dashboard":
        # 👇 SOLO aquí entramos al dashboard de empresa
        company_dashboard.render()

    else:
        st.error("Página no encontrada para empresa.")


# -------------------------
# Router principal por rol
# -------------------------
def render_portal():
    role = st.session_state.role

    render_sidebar_navigation()

    if role == "candidate":
        render_candidate_portal()
    elif role == "company":
        render_company_portal()
    else:
        st.error(
            "No se ha podido determinar tu rol. Por favor, cierra sesión e inténtalo de nuevo."
        )


# -------------------------
# Main
# -------------------------
def main():
    st.set_page_config(
        page_title="MatchKey",
        page_icon="🟣",
        layout="wide",
    )
    apply_accenture_theme()
    init_session_state()

    if not st.session_state.auth["is_authenticated"]:
        # Vista pública
        render_public_landing()
        render_login_card()
    else:
        # Vista privada por rol
        render_private_header()
        render_portal()


if __name__ == "__main__":
    main()
