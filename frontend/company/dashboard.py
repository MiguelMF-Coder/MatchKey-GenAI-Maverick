import streamlit as st

def render():
    st.markdown("## 📊 Dashboard Empresa")

    st.write(
        "Aquí mostraremos métricas globales: calidad de candidatos por vacante, "
        "encaje cultural, Co-Teaching, y analíticas agregadas de talento."
    )

    # TODO: aquí se conectará con:
    # - /jobs/{id}/match_candidates
    # - /jobs/{id}/co_teaching
    # - /companies/{id}/profile
    # - Endpoints de analítica de talento
