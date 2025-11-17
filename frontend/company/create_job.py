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


def create_job(company_id, job_data, uploaded_file=None):
    """
    Crea una vacante en el backend.
    - Si hay fichero, se envía como multipart (file + campos en form-data).
    - Si no, se envía JSON.
    Suponemos que /jobs/create puede:
      - Crear la vacante
      - (Opcionalmente) ejecutar OCR + Skills Extractor
    y devolver algo como:
      {
        "job_id": ...,
        "must_have": [...],
        "nice_to_have": [...],
        "all_skills": [...],
        ...
      }
    """
    url = f"{BACKEND_URL}/jobs/create"

    # Añadimos el company_id al payload
    job_data["company_id"] = company_id

    try:
        if uploaded_file is not None:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            # Para multipart usaremos "data" en lugar de "json"
            resp = requests.post(url, data=job_data, files=files, timeout=60)
        else:
            resp = requests.post(url, json=job_data, timeout=60)
    except Exception as e:
        st.error(f"Error al crear la vacante en el backend: {e}")
        return None

    if resp.status_code not in (200, 201):
        st.error(
            f"No se ha podido crear la vacante. Código: {resp.status_code}"
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
    st.markdown("## 📄 Crear nueva vacante")
    st.caption(
        "Define los datos básicos de la vacante, sube o pega la descripción del puesto "
        "y describe el equipo en el que trabajará la persona para optimizar el matching."
    )

    company_id = ensure_company_id()
    if not company_id:
        st.stop()

    with st.form("create_job_form"):
        # -------------------------
        # Fila 1: datos básicos de la vacante
        # -------------------------
        st.markdown("### 📝 Datos básicos")

        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input(
                "Título del puesto",
                placeholder="Ej. Data Analyst, Backend Developer, Product Manager...",
            )
            department = st.text_input(
                "Departamento / área",
                placeholder="Ej. Data & Analytics, Tecnología, Producto...",
            )
            location = st.text_input(
                "Ubicación / modalidad",
                placeholder="Ej. Madrid (híbrido), 100% remoto, Barcelona presencial...",
            )
            contract_type = st.text_input(
                "Tipo de contrato",
                placeholder="Ej. Indefinido, prácticas, temporal, freelance...",
            )

        with col2:
            salary_range = st.text_input(
                "Rango salarial (opcional)",
                placeholder="Ej. 28k–35k, 40k–50k...",
            )
            seniority = st.selectbox(
                "Seniority objetivo",
                ["No especificado", "Junior", "Mid", "Senior", "Lead"],
            )
            is_remote_friendly = st.checkbox(
                "Permite trabajo en remoto (al menos parcial)",
                value=False,
            )

        st.markdown("---")

        # -------------------------
        # Fila 2: Descripción del puesto (JD)
        # -------------------------
        st.markdown("### 📄 Descripción del puesto (JD)")

        jd_col1, jd_col2 = st.columns(2)

        with jd_col1:
            uploaded_file = st.file_uploader(
                "Subir JD en PDF / DOCX (opcional)",
                type=["pdf", "docx", "doc"],
                help="Puedes subir la descripción del puesto y la IA extraerá las skills.",
            )

        with jd_col2:
            jd_text = st.text_area(
                "O pega aquí la descripción del puesto",
                height=200,
                placeholder="Pega aquí el texto de la oferta si no la tienes en PDF/DOCX.",
            )

        st.caption(
            "Puedes usar cualquiera de las dos opciones (fichero o texto). "
            "Si usas ambas, se dará prioridad al fichero."
        )

        st.markdown("---")

        # -------------------------
        # Fila 3: Equipo en el que va a trabajar
        # -------------------------
        st.markdown("### 🧩 Equipo en el que va a trabajar")

        team_name = st.text_input(
            "Nombre del equipo (interno)",
            placeholder="Ej. Equipo de Data & Analytics, Squad de Producto Growth...",
        )
        team_mission = st.text_area(
            "Misión del equipo",
            height=100,
            placeholder="Explica brevemente qué hace este equipo dentro de la empresa.",
        )

        team_work_style = st.selectbox(
            "Ritmo y forma de trabajo del equipo",
            [
                "No especificado",
                "Ritmo alto, muy orientado a resultados",
                "Ritmo estable, foco en calidad y procesos",
                "Muy experimental / creativo",
                "Entorno muy cambiante, alta incertidumbre",
            ],
        )

        team_communication = st.selectbox(
            "Estilo de comunicación del equipo",
            [
                "No especificado",
                "Muy directa y honesta",
                "Más diplomática y cuidada",
                "Principalmente escrita (Slack / email)",
                "Principalmente oral (reuniones frecuentes)",
            ],
        )

        team_autonomy = st.selectbox(
            "Nivel de autonomía esperado del nuevo miembro",
            [
                "No especificado",
                "Alta autonomía desde el primer día",
                "Autonomía progresiva, con acompañamiento inicial",
                "Trabajo muy guiado y estructurado",
            ],
        )

        team_ideal_profile = st.text_area(
            "¿Qué tipo de persona encaja mejor en este equipo?",
            height=120,
            placeholder=(
                "Ej. Personas que disfrutan del feedback directo, con ganas de aprender, "
                "que se sienten cómodas en entornos cambiantes y valoran el trabajo en equipo."
            ),
        )

        st.markdown("#### 👥 Perfiles individuales del equipo")

        num_members = st.number_input(
            "Número de personas clave del equipo (con las que esta persona trabajará más de cerca)",
            min_value=0,
            max_value=10,
            value=0,
            step=1,
        )

        team_members = []
        for i in range(num_members):
            st.markdown(f"##### Miembro {i + 1}")
            m_col1, m_col2 = st.columns(2)

            with m_col1:
                role = st.text_input(
                    f"Rol del miembro {i + 1}",
                    key=f"member_role_{i}",
                    placeholder="Ej. Tech Lead, Data Analyst, Product Manager...",
                )
                seniority_member = st.selectbox(
                    f"Seniority del miembro {i + 1}",
                    ["No especificado", "Junior", "Mid", "Senior", "Lead"],
                    key=f"member_seniority_{i}",
                )
                work_style_member = st.selectbox(
                    f"Estilo de trabajo del miembro {i + 1}",
                    [
                        "No especificado",
                        "Muy estructurado",
                        "Flexible / adaptable",
                        "Muy creativo / caótico",
                    ],
                    key=f"member_work_style_{i}",
                )

            with m_col2:
                communication_member = st.selectbox(
                    f"Estilo de comunicación del miembro {i + 1}",
                    [
                        "No especificado",
                        "Directo y sin rodeos",
                        "Cuidadoso y diplomático",
                        "Prefiere comunicación escrita",
                        "Prefiere comunicación oral",
                    ],
                    key=f"member_comm_style_{i}",
                )
                values_member = st.text_input(
                    f"Valores / prioridades de este miembro {i + 1}",
                    key=f"member_values_{i}",
                    placeholder="Ej. aprendizaje, estabilidad, impacto, trabajo en equipo...",
                )
                collab_style_member = st.text_input(
                    f"Estilo de colaboración con el nuevo miembro {i + 1}",
                    key=f"member_collab_{i}",
                    placeholder="Ej. me gusta mentorizar, prefiero trabajar en paralelo, etc.",
                )

            team_members.append(
                {
                    "role": role,
                    "seniority": seniority_member,
                    "work_style": work_style_member,
                    "communication_style": communication_member,
                    "values": values_member,
                    "collaboration_style": collab_style_member,
                }
            )

            st.markdown("---")

        st.markdown("### ✅ Confirmación")

        auto_extract_skills = st.checkbox(
            "Dejar que la IA analice la descripción del puesto para extraer skills Must/Nice",
            value=True,
        )

        submitted = st.form_submit_button("Crear vacante con IA")

    # -------------------------
    # Envío al backend
    # -------------------------
    if submitted:
        if not title:
            st.error("El título del puesto es obligatorio.")
            return

        if uploaded_file is None and not jd_text.strip():
            st.error(
                "Debes subir un JD en fichero o pegar la descripción del puesto en texto."
            )
            return

        # Construimos el payload de la vacante
        job_data = {
            "title": title,
            "department": department,
            "location": location,
            "contract_type": contract_type,
            "salary_range": salary_range,
            "seniority": seniority,
            "is_remote_friendly": is_remote_friendly,
            "jd_text": jd_text if uploaded_file is None else None,
            "auto_extract_skills": auto_extract_skills,
            "team_profile": {
                "team_name": team_name,
                "team_mission": team_mission,
                "team_work_style": team_work_style,
                "team_communication": team_communication,
                "team_autonomy": team_autonomy,
                "team_ideal_profile": team_ideal_profile,
                "members": team_members,
            },
        }

        with st.spinner("Creando la vacante y analizando la información con IA..."):
            result = create_job(company_id, job_data, uploaded_file)

        if result:
            st.success("Vacante creada correctamente ✅")

            job_id = result.get("job_id") or result.get("id")
            if job_id:
                st.caption(f"ID de la vacante en el sistema: {job_id}")

            # Mostramos skills extraídas si el backend las ha devuelto
            must_have = (
                result.get("must_have")
                or result.get("must_skills")
            )
            nice_to_have = result.get("nice_to_have")
            all_skills = result.get("all_skills")

            if auto_extract_skills and (must_have or nice_to_have or all_skills):
                st.markdown("### 🧩 Skills detectadas por la IA")

                if all_skills:
                    st.markdown("**Listado general de skills detectadas:**")
                    if isinstance(all_skills, list):
                        st.write(", ".join(all_skills))
                    else:
                        st.write(all_skills)

                col_m1, col_m2 = st.columns(2)

                with col_m1:
                    if must_have:
                        st.markdown("#### ✅ Must-have (imprescindibles)")
                        if isinstance(must_have, list):
                            for s in must_have:
                                st.write(f"- {s}")
                        else:
                            st.write(must_have)

                with col_m2:
                    if nice_to_have:
                        st.markdown("#### ⭐ Nice-to-have (valorables)")
                        if isinstance(nice_to_have, list):
                            for s in nice_to_have:
                                st.write(f"- {s}")
                        else:
                            st.write(nice_to_have)

            st.markdown("---")
            st.markdown(
                "La vacante ya está lista para usarse en el motor de matching, analíticas "
                "y en el módulo de Co-Teaching."
            )
