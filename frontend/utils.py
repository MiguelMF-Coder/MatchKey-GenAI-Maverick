# frontend/utils.py
import os
import streamlit as st
import requests

def get_backend_url() -> str:
    url = os.environ.get("BACKEND_URL")
    if url:
        return url

    # Fallback local
    return "http://localhost:8000"


def apply_accenture_theme():
    """
    Estilos custom tipo Accenture: morado, oscuro, limpio.
    """
    accent_color = "#A100FF"   # Morado Accenture
    dark_bg = "#0B0318"
    card_bg = "#1A1030"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: radial-gradient(circle at top left, {accent_color}22, {dark_bg});
            color: #FFFFFF;
        }}

        .mk-title {{
            font-size: 3rem;
            font-weight: 800;
            color: {accent_color};
            margin-bottom: 0.2rem;
        }}

        .mk-subtitle {{
            font-size: 1.1rem;
            color: #E0D7FF;
            margin-bottom: 2rem;
        }}

        .mk-section-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #FFFFFF;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }}

        .mk-text {{
            font-size: 0.95rem;
            color: #E5E1FF;
        }}

        .mk-card {{
            background: {card_bg};
            border-radius: 16px;
            padding: 1rem 1.3rem;
            box-shadow: 0 12px 30px rgba(0,0,0,0.4);
            border: 1px solid {accent_color}33;
            margin-bottom: 0.7rem;
        }}

        .mk-badge {{
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 999px;
            background: {accent_color}33;
            color: #F5F0FF;
            font-size: 0.75rem;
        }}

        .mk-footer {{
            margin-top: 2rem;
            font-size: 0.85rem;
            color: #C9C2FF;
            text-align: center;
        }}

        .stButton>button {{
            background: linear-gradient(90deg, {accent_color}, #5A00B3);
            color: white;
            border-radius: 999px;
            border: none;
            padding: 0.6rem 1rem;
            font-weight: 600;
        }}

        .stButton>button:hover {{
            filter: brightness(1.05);
            box-shadow: 0 0 0 1px {accent_color}AA;
        }}

        .stTextInput>div>div>input,
        .stSelectbox>div>div>div>div,
        .stTextArea textarea {{
            background-color: #241637;
            color: #F5F0FF;
            border-radius: 10px;
        }}

        .stFileUploader>div>div {{
            background-color: #241637;
            border-radius: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_session_state():
    defaults = {
        "role": None,          # "candidate" / "company"
        "user_name": None,
        "candidate_id": 1,     # ids demo
        "company_id": 1,
        "recommended_jobs": [],
        "selected_job_for_improvement": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def api_get(path: str, params: dict | None = None):
    base_url = get_backend_url()
    url = f"{base_url}{path}"
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        return res.json(), None
    except Exception as e:
        return None, str(e)


def api_post(path: str, json: dict | None = None):
    base_url = get_backend_url()
    url = f"{base_url}{path}"
    try:
        res = requests.post(url, json=json, timeout=10)
        res.raise_for_status()
        return res.json(), None
    except Exception as e:
        return None, str(e)


def require_role(expected_role: str):
    role = st.session_state.get("role")
    if role is None:
        st.warning("Primero selecciona tu rol en la pantalla de inicio.")
        st.stop()
    if role != expected_role:
        st.error("No tienes acceso a este portal con el rol actual.")
        st.stop()


def sidebar_header():
    """
    Muestra info básica en el sidebar (nombre y rol) y botón de 'cerrar sesión'.
    """
    role = st.session_state.get("role")
    user_name = st.session_state.get("user_name") or "Usuario demo"

    role_label = "Candidato" if role == "candidate" else "Empresa"
    st.sidebar.markdown(f"**👤 {user_name}**")
    st.sidebar.markdown(f"**Rol:** {role_label}")

    if st.sidebar.button("Cerrar sesión"):
        for key in ["role", "user_name", "candidate_id", "company_id", "recommended_jobs"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
