import streamlit as st
from utils import apply_accenture_theme
from utils import get_backend_url
from utils import api_post  # ⬅️ IMPORTAMOS EL HELPER PARA LLAMAR AL BACKEND

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
# RUTAS OPCIONALES DE IMÁGENES
# -------------------------
SIDEBAR_PHOTO_PATH = "images/banner_barra_lateral.png"              # Foto en menú lateral
LOGIN_BANNER_PATH = "images/banner_inicio_sesion.png"               # Banner superior en pantalla de login
HOME_ILLUSTRATION_PATH = "images/candidate_home_illustration.png"   # Ilustración en home candidato
COMPANY_HOME_ILLUSTRATION_PATH = "images/company_home_illustration.png"  # Ilustración en home empresa


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
    if "candidate_id" not in st.session_state:
        st.session_state.candidate_id = None
    if "company_id" not in st.session_state:
        st.session_state.company_id = None


# -------------------------
# UI Pública (Landing)
# -------------------------
def render_public_landing():
    # Estilos para hacer la landing más visual
    st.markdown(
        """
        <style>
        .mk-main-wrapper {
            max-width: 1100px;
            margin: 0 auto;  /* centra todo el contenido (banner + hero) */
        }
        .mk-hero {
            padding: 2.5rem 2rem 1rem 2rem;
            border-radius: 20px;
            background: radial-gradient(circle at top left, rgba(161,0,255,0.35), transparent),
                        radial-gradient(circle at bottom right, rgba(0,200,255,0.25), transparent);
            border: 1px solid rgba(255,255,255,0.06);
            box-shadow: 0 18px 40px rgba(0,0,0,0.55);
            margin-bottom: 1.8rem;
        }
        .mk-hero-title {
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.3rem;
        }
        .mk-hero-subtitle {
            font-size: 1.05rem;
            opacity: 0.82;
            max-width: 620px;
        }
        .mk-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.8rem;
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            background: rgba(161,0,255,0.18);
            border: 1px solid rgba(161,0,255,0.4);
            margin-bottom: 0.8rem;
        }
        .mk-role-card {
            background-color: rgba(15,15,15,0.9);
            border-radius: 16px;
            padding: 1.2rem 1.1rem;
            border: 1px solid rgba(255,255,255,0.06);
            box-shadow: 0 10px 30px rgba(0,0,0,0.55);
        }
        .mk-role-title {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.4rem;
        }
        .mk-role-list {
            font-size: 0.95rem;
            opacity: 0.9;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="mk-hero">
            <div class="mk-pill">🟣 MatchKey · IA para talento y cultura</div>
            <div class="mk-hero-title">Encuentra el trabajo (o el talento) que encaja de verdad contigo.</div>
            <div class="mk-hero-subtitle">
                MatchKey es un portal de empleo inteligente que conecta <b>personas</b> y <b>empresas</b>
                no solo por habilidades, sino también por <b>valores</b>, <b>cultura</b> y <b>encaje de equipo</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="mk-role-card">
                <div class="mk-role-title">👤 Soy Candidato</div>
                <div class="mk-role-list">
                <ul>
                    <li>Sube tu <b>CV</b> una sola vez</li>
                    <li>Deja que la IA detecte tus <b>skills</b></li>
                    <li>Descubre vacantes <b>alineadas contigo</b></li>
                    <li>Identifica <b>gaps</b> y recibe recomendaciones de <b>cursos</b></li>
                </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="mk-role-card">
                <div class="mk-role-title">🏢 Soy Empresa</div>
                <div class="mk-role-list">
                <ul>
                    <li>Define tu <b>cultura</b> y <b>valores</b></li>
                    <li>Publica tus <b>vacantes</b> fácilmente</li>
                    <li>Deja que el motor de matching puntúe candidatos</li>
                    <li>Explora <b>Co-Teaching</b> y analíticas de talento</li>
                </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")


# -------------------------
# Formulario de Login (real contra backend)
# -------------------------
def render_login_card():
    # Estilo para el formulario de login como tarjeta centrada
    st.markdown(
        """
        <style>
        .mk-login-container {
            max-width: 520px;
            margin: 0 auto 2.5rem auto;
        }
        .mk-login-title {
            text-align: center;
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        .mk-login-subtitle {
            text-align: center;
            font-size: 0.95rem;
            opacity: 0.7;
            margin-bottom: 1rem;
        }
        .stForm {
            background-color: rgba(15, 15, 15, 0.94);
            border-radius: 18px;
            padding: 1.5rem 1.4rem 1.1rem 1.4rem;
            box-shadow: 0 16px 40px rgba(0,0,0,0.7);
            border: 1px solid rgba(255,255,255,0.06);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="mk-login-container">
            <div class="mk-login-title">Inicia sesión en MatchKey</div>
            <div class="mk-login-subtitle">
                Accede a tu portal de candidato o empresa con un solo login.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

        # Convertimos la elección visual en el rol real usado por el backend
        role = "candidate" if "Candidato" in role_choice else "company"

        payload = {
            "email": email,
            "password": password,
            "role": role,
        }

        # 🚀 Llamada REAL al backend: POST /auth/login
        data, error = api_post("/auth/login", json=payload)

        if error:
            st.error(f"Error al iniciar sesión: {error}")
            return

        # data debe contener: user_id, email, role, candidate_id, company_id
        st.session_state.auth["is_authenticated"] = True
        st.session_state.auth["user_id"] = data.get("user_id")
        st.session_state.auth["email"] = data.get("email")
        st.session_state.role = data.get("role")

        # Guardamos los IDs específicos según el rol
        if st.session_state.role == "candidate":
            st.session_state.candidate_id = data.get("candidate_id")
            st.session_state.company_id = None
        else:
            st.session_state.company_id = data.get("company_id")
            st.session_state.candidate_id = None

        st.session_state.current_page = "Inicio"

        # Forzamos recarga para entrar en el portal
        st.success("Inicio de sesión correcto. Cargando tu portal...")
        st.rerun()


# -------------------------
# Header privado (cuando ya hay sesión)
# -------------------------
def render_private_header():
    role = st.session_state.role
    email = st.session_state.auth.get("email")

    st.markdown(
        """
        <style>
        .mk-header {
            padding: 0.6rem 0.4rem 0.1rem 0.4rem;
            margin-bottom: 0.4rem;
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }
        .mk-header-title {
            font-size: 1.4rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .mk-header-sub {
            font-size: 0.85rem;
            opacity: 0.7;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([3, 1])

    with left:
        st.markdown('<div class="mk-header">', unsafe_allow_html=True)
        if role == "candidate":
            st.markdown(
                '<div class="mk-header-title">👤 Portal Candidato</div>',
                unsafe_allow_html=True,
            )
        elif role == "company":
            st.markdown(
                '<div class="mk-header-title">🏢 Portal Empresa</div>',
                unsafe_allow_html=True,
            )

        if email:
            st.markdown(
                f'<div class="mk-header-sub">Conectado como: <b>{email}</b></div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

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
            st.session_state.candidate_id = None
            st.session_state.company_id = None
            st.rerun()


# -------------------------
# Menú lateral por rol
# -------------------------
def render_sidebar_navigation():
    role = st.session_state.role

    with st.sidebar:
        # Estilos del sidebar (imagen + botones)
        st.markdown(
            """
            <style>
            .mk-sidebar-section {
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.18em;
                opacity: 0.8;
                margin-top: 0.6rem;
                margin-bottom: 0.6rem;
                text-align: center;
                font-weight: 600;
            }
            .sidebar-logo-container {
                display: flex;
                justify-content: center;
                margin-top: 0.2rem;
                margin-bottom: 0.8rem;
            }

            /* Botones de navegación (radio) en forma de pill, ocupando todo el ancho */
            [data-testid="stSidebar"] div[role='radiogroup'] {
                width: 100%;
            }
            [data-testid="stSidebar"] div[role='radiogroup'] > label {
                display: block;
                width: 100%;
                box-sizing: border-box;
                border-radius: 999px;
                padding: 0.40rem 0.85rem;
                margin-bottom: 0.28rem;
                border: 1px solid rgba(255,255,255,0.05);
                background: rgba(0,0,0,0.18);
                cursor: pointer;
            }
            [data-testid="stSidebar"] div[role='radiogroup'] > label:hover {
                border-color: rgba(161,0,255,0.7);
                background: linear-gradient(90deg, rgba(161,0,255,0.35), rgba(0,0,0,0.45));
            }
            /* Ocultamos el círculo del radio */
            [data-testid="stSidebar"] div[role='radiogroup'] > label > div:first-child {
                display: none !important;
            }
            /* Estado seleccionado (si el navegador soporta :has) */
            [data-testid="stSidebar"] div[role='radiogroup'] > label:has(input:checked) {
                border-color: #A100FF;
                background: linear-gradient(90deg, #A100FF, #4B0082);
                box-shadow: 0 0 0 1px rgba(0,0,0,0.4);
            }
            [data-testid="stSidebar"] div[role='radiogroup'] > label span {
                font-size: 0.9rem;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Imagen principal del sidebar como branding (sin texto)
        if SIDEBAR_PHOTO_PATH:
            st.markdown('<div class="sidebar-logo-container">', unsafe_allow_html=True)
            st.image(SIDEBAR_PHOTO_PATH, use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Navegación
        st.markdown(
            '<div class="mk-sidebar-section">─── NAVEGACIÓN ───</div>',
            unsafe_allow_html=True,
        )

        if role == "candidate":
            opciones = [
                "Inicio",
                "Mi perfil",
                "Llamada IA",
                "Vacantes recomendadas",
                "Mejora (gaps + cursos)",
                "Dashboard",
            ]
            page = st.radio(
                "Secciones",
                opciones,
                index=opciones.index(st.session_state.current_page)
                if st.session_state.current_page in opciones
                else 0,
            )
        else:  # company
            opciones = [
                "Inicio",
                "Perfil empresa",
                "Portal vacantes",
                "Analítica de talento",
                "Co-Teaching",
                "Dashboard",
            ]
            page = st.radio(
                "Secciones",
                opciones,
                index=opciones.index(st.session_state.current_page)
                if st.session_state.current_page in opciones
                else 0,
            )

        st.session_state.current_page = page


# -------------------------
# Contenido de cada portal
# -------------------------
def render_candidate_portal():
    page = st.session_state.current_page

    if page == "Inicio":
        # Tarjeta de bienvenida más rica + descripción de la app + imagen
        st.markdown(
            """
            <style>
            .mk-home-card {
                background-color: rgba(15,15,15,0.95);
                border-radius: 18px;
                padding: 1.5rem 1.4rem;
                border: 1px solid rgba(255,255,255,0.06);
                box-shadow: 0 18px 40px rgba(0,0,0,0.7);
                margin-top: 0.2rem;
                margin-bottom: 1.2rem;
            }
            .mk-home-title {
                font-size: 1.4rem;
                font-weight: 700;
                margin-bottom: 0.4rem;
            }
            .mk-home-sub {
                font-size: 0.95rem;
                opacity: 0.85;
                margin-bottom: 0.8rem;
            }
            .mk-home-bullets {
                font-size: 0.9rem;
                opacity: 0.85;
            }
            .mk-home-feature-title {
                font-weight: 600;
                margin-bottom: 0.15rem;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        col_main, col_img = st.columns([2, 1])

        with col_main:
            st.markdown(
                """
                <div class="mk-home-card">
                    <div class="mk-home-title">👋 Bienvenido/a a tu espacio MatchKey</div>
                    <div class="mk-home-sub">
                        Este es tu panel personal para gestionar tu búsqueda de empleo con ayuda de la IA.
                        MatchKey analiza tu CV, tus respuestas y tus preferencias para encontrar vacantes
                        que encajen contigo no solo por skills, sino también por valores y forma de trabajar.
                    </div>
                    <div class="mk-home-bullets">
                        <ul>
                            <li><b>Descubre vacantes recomendadas</b> en función de tu perfil y tu encaje cultural.</li>
                            <li><b>Identifica tus gaps</b> y recibe sugerencias de cursos concretos para mejorarlos.</li>
                            <li><b>Comprende tu perfil</b> con el resumen psicológico-profesional generado por la IA.</li>
                        </ul>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_img:
            if HOME_ILLUSTRATION_PATH:
                st.markdown(
                    '<div style="display:flex; align-items:center; height:100%; padding-top:10px;">',
                    unsafe_allow_html=True,
                )
                st.image(HOME_ILLUSTRATION_PATH, use_column_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**🧠 IA que te conoce**")
            st.caption(
                "Completa la Llamada IA para que el sistema entienda tus motivaciones, valores y forma de trabajar."
            )
            if st.button("Hacer Llamada IA"):
                st.session_state.current_page = "Llamada IA"
                st.rerun()

        with col2:
            st.markdown("**💼 Vacantes recomendadas**")
            st.caption(
                "Explora puestos que ya vienen filtrados por encaje de skills, valores y team-fit."
            )
            if st.button("Ver vacantes recomendadas"):
                st.session_state.current_page = "Vacantes recomendadas"
                st.rerun()

        with col3:
            st.markdown("**📈 Mejora tu perfil**")
            st.caption(
                "Revisa tus gaps por vacante y sigue las recomendaciones de cursos para subir tu match."
            )
            if st.button("Ir a Mejora (gaps + cursos)"):
                st.session_state.current_page = "Mejora (gaps + cursos)"
                st.rerun()

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
        # Tarjeta de bienvenida empresa más rica + posible ilustración
        st.markdown(
            """
            <style>
            .mk-home-card {
                background-color: rgba(15,15,15,0.95);
                border-radius: 18px;
                padding: 1.5rem 1.4rem;
                border: 1px solid rgba(255,255,255,0.06);
                box-shadow: 0 18px 40px rgba(0,0,0,0.7);
                margin-top: 0.2rem;
                margin-bottom: 1.2rem;
            }
            .mk-home-title {
                font-size: 1.4rem;
                font-weight: 700;
                margin-bottom: 0.4rem;
            }
            .mk-home-sub {
                font-size: 0.95rem;
                opacity: 0.85;
                margin-bottom: 0.8rem;
            }
            .mk-home-bullets {
                font-size: 0.9rem;
                opacity: 0.85;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        col_main, col_img = st.columns([2, 1])

        with col_main:
            st.markdown(
                """
                <div class="mk-home-card">
                    <div class="mk-home-title">👋 Bienvenido/a al portal empresa de MatchKey</div>
                    <div class="mk-home-sub">
                        Desde aquí puedes definir tu cultura, crear vacantes y dejar que nuestra IA te ayude
                        a encontrar talento que encaje con tu forma de trabajar y con los equipos existentes.
                    </div>
                    <div class="mk-home-bullets">
                        <ul>
                            <li><b>Define el perfil de tu empresa</b> con valores, cultura y forma de trabajo.</li>
                            <li><b>Crea vacantes</b> y deja que el motor de matching priorice a los mejores candidatos.</li>
                            <li><b>Explora Co-Teaching</b> para descubrir parejas de candidatos complementarios.</li>
                        </ul>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_img:
            if COMPANY_HOME_ILLUSTRATION_PATH:
                st.markdown(
                    '<div style="display:flex; align-items:center; height:100%; padding-top:10px;">',
                    unsafe_allow_html=True,
                )
                st.image(COMPANY_HOME_ILLUSTRATION_PATH, use_column_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**📄 Completar perfil de empresa**")
            st.caption("Empieza definiendo quién eres y qué tipo de personas encajan mejor.")
            if st.button("Ir al perfil de empresa"):
                st.session_state.current_page = "Perfil empresa"
                st.rerun()

        with col2:
            st.markdown("**➕ Crear una nueva vacante**")
            st.caption("Publica una posición y deja que el sistema te sugiera candidatos.")
            if st.button("Crear vacante"):
                st.session_state.current_page = "Crear vacante"
                st.rerun()

        with col3:
            st.markdown("**📊 Ver analítica de talento**")
            st.caption("Consulta la distribución de encaje y descubre insights sobre tus vacantes.")
            if st.button("Ir a Analítica de talento"):
                st.session_state.current_page = "Analítica de talento"
                st.rerun()

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
        # Contenedor común para banner + landing, con mismo ancho
        st.markdown('<div class="mk-main-wrapper">', unsafe_allow_html=True)

        # 🔝 Banner centrado con ancho moderado
        if LOGIN_BANNER_PATH:
            st.markdown(
                """
                <div style="display:flex; justify-content:center; margin-top:0.5rem; margin-bottom:1.2rem;">
                """,
                unsafe_allow_html=True,
            )
            st.image(LOGIN_BANNER_PATH, width=780)
            st.markdown("</div>", unsafe_allow_html=True)

        # Vista pública
        render_public_landing()
        render_login_card()

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Vista privada por rol
        render_private_header()
        render_portal()


if __name__ == "__main__":
    main()
