import streamlit as st
import requests
from utils import get_backend_url

BACKEND_URL = get_backend_url()


# -------------------------
# Helpers de sesión / auth
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
        try:
            st.json(resp.json())
        except Exception:
            st.write(resp.text)
        return None

    data = resp.json()
    company_id = data.get("id") or data.get("company_id")

    if not company_id:
        st.error("El backend no devolvió un company_id válido.")
        return None

    st.session_state.company_id = company_id
    return company_id


# -------------------------
# Helpers de backend (API)
# -------------------------
def create_job(company_id, job_data, uploaded_file=None):
    """
    Crea una vacante en el backend.
    - Si hay fichero, se envía como multipart (file + campos en form-data).
    - Si no, se envía JSON.
    """
    url = f"{BACKEND_URL}/jobs/create"

    # Añadimos el company_id al payload
    job_data["company_id"] = company_id

    try:
        if uploaded_file is not None:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            # Para multipart usamos "data" en lugar de "json"
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


def fetch_company_jobs_with_applications(company_id):
    url = f"{BACKEND_URL}/companies/{company_id}/jobs_with_applications"
    try:
        resp = requests.get(url, timeout=15)
    except Exception as e:
        st.error(f"Error al obtener las vacantes de la empresa: {e}")
        return None

    if resp.status_code != 200:
        st.error(
            f"No se han podido obtener las vacantes. Código: {resp.status_code}"
        )
        try:
            st.json(resp.json())
        except Exception:
            st.write(resp.text)
        return None

    return resp.json()


def fetch_job_applications(job_id):
    """
    Devuelve las candidaturas de una vacante.

    Se espera que el backend devuelva algo del estilo:
    {
        "applications": [
            {
                "application_id": int,
                "candidate_id": int,        # ⚠️ Ideal para matching
                "candidate_name": str,
                "candidate_email": str,
                "applied_at": str,
                "status": str,
                ...
            },
            ...
        ]
    }
    """
    url = f"{BACKEND_URL}/jobs/{job_id}/applications"
    try:
        resp = requests.get(url, timeout=15)
    except Exception as e:
        st.error(f"Error al obtener las candidaturas de la vacante: {e}")
        return None

    if resp.status_code != 200:
        st.error(
            f"No se han podido obtener las candidaturas. Código: {resp.status_code}"
        )
        try:
            st.json(resp.json())
        except Exception:
            st.write(resp.text)
        return None

    return resp.json()


def fetch_matching_scores(candidate_id, job_id):
    """
    Llama al endpoint real de matching:
    GET /matching/candidates/{candidate_id}/job/{job_id}/scores

    Se espera algo como:
    {
        "skills_fit": 80.0,
        "values_fit": 70.0,
        "team_fit": 65.0,
        "global_fit": 75.0
    }
    """
    if candidate_id is None:
        return None

    url = f"{BACKEND_URL}/matching/candidates/{candidate_id}/job/{job_id}/scores"
    try:
        resp = requests.get(url, timeout=10)
    except Exception as e:
        st.error(f"Error al obtener el matching para el candidato {candidate_id}: {e}")
        return None

    if resp.status_code != 200:
        # No lo tratamos como error bloqueante, simplemente no mostramos matching
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        st.warning(
            f"No se han podido obtener los scores de matching "
            f"para el candidato {candidate_id}. Detalle: {err}"
        )
        return None

    return resp.json()


def fetch_candidate_profile(candidate_id):
    """
    Carga un resumen del candidato para mostrarlo en el portal de empresa.
    GET /candidates/{id}/profile

    Se espera algo tipo:
    {
        "id": ...,
        "full_name": ...,
        "headline": ...,
        "location": ...,
        "years_experience": ...,
        "skills": [...],
        ...
    }
    """
    if candidate_id is None:
        return None

    url = f"{BACKEND_URL}/candidates/{candidate_id}/profile"
    try:
        resp = requests.get(url, timeout=10)
    except Exception as e:
        st.error(f"Error al obtener el perfil del candidato {candidate_id}: {e}")
        return None

    if resp.status_code != 200:
        # Igual que en matching: no bloqueamos, solo avisamos si queremos
        return None

    return resp.json()


def select_application_backend(job_id, application_id):
    url = f"{BACKEND_URL}/jobs/{job_id}/applications/{application_id}/select"
    try:
        resp = requests.post(url, timeout=20)
    except Exception as e:
        st.error(f"Error al seleccionar la candidatura: {e}")
        return None

    if resp.status_code not in (200, 201):
        st.error(
            f"No se ha podido seleccionar la candidatura. Código: {resp.status_code}"
        )
        try:
            st.json(resp.json())
        except Exception:
            st.write(resp.text)
        return None

    return resp.json()


def update_job_backend(job_id, payload):
    url = f"{BACKEND_URL}/jobs/{job_id}"
    try:
        resp = requests.put(url, json=payload, timeout=20)
    except Exception as e:
        st.error(f"Error al actualizar la vacante: {e}")
        return None

    if resp.status_code not in (200, 201):
        st.error(
            f"No se ha podido actualizar la vacante. Código: {resp.status_code}"
        )
        try:
            st.json(resp.json())
        except Exception:
            st.write(resp.text)
        return None

    return resp.json()


def delete_job_backend(job_id):
    url = f"{BACKEND_URL}/jobs/{job_id}"
    try:
        resp = requests.delete(url, timeout=20)
    except Exception as e:
        st.error(f"Error al eliminar la vacante: {e}")
        return None

    if resp.status_code not in (200, 204):
        st.error(
            f"No se ha podido eliminar la vacante. Código: {resp.status_code}"
        )
        try:
            st.json(resp.json())
        except Exception:
            st.write(resp.text)
        return None

    try:
        return resp.json()
    except Exception:
        return {"status": "ok", "message": "Vacante eliminada"}


# -------------------------
# UI: Crear nueva vacante
# -------------------------
def render_create_job_tab(company_id):
    st.markdown("## 📄 Crear nueva vacante")
    st.caption(
        "Define los datos básicos de la vacante, sube o pega la descripción del puesto "
        "y describe el equipo en el que trabajará la persona para optimizar el matching."
    )

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

            # Flag para refrescar la pestaña de gestión
            st.session_state["refresh_company_jobs"] = True


# -------------------------
# UI: Gestión de vacantes
# -------------------------

def render_manage_jobs_tab(company_id):
    import streamlit as st

    st.markdown("## 📊 Gestionar mis vacantes")
    st.caption(
        "Revisa tus vacantes, ve cuántos candidatos han aplicado, su encaje con la oferta, "
        "selecciona personas, edita los detalles o elimina ofertas que ya no estén activas."
    )

    if st.session_state.get("refresh_company_jobs"):
        st.session_state["refresh_company_jobs"] = False

    data = fetch_company_jobs_with_applications(company_id)
    if not data:
        return

    jobs = data.get("jobs", [])
    if not jobs:
        st.info("Todavía no has creado ninguna vacante. Empieza en la pestaña 'Crear vacante'.")
        return

    for job in jobs:
        job_id = job.get("job_id")
        title = job.get("title") or "Sin título"
        location = job.get("location") or "Ubicación no especificada"
        department = job.get("department") or "Departamento no especificado"
        status = job.get("status") or "sin estado"
        created_at = job.get("created_at")
        app_count = job.get("application_count", 0)

        with st.expander(f"📌 {title}"):
            # Resumen
            col_a, col_b, col_c = st.columns([2,2,1])
            with col_a:
                st.markdown(f"**Ubicación:** {location}")
                st.markdown(f"**Departamento:** {department}")
            with col_b:
                st.markdown(f"**Estado:** `{status}`")
                st.markdown(f"**Candidatos aplicados:** {app_count}")
                if created_at:
                    st.caption(f"Creada: {created_at}")
            with col_c:
                if st.button("🗑️ Eliminar vacante", key=f"delete_job_{job_id}"):
                    res = delete_job_backend(job_id)
                    if res:
                        st.success("Vacante eliminada correctamente.")
                        st.session_state["refresh_company_jobs"] = True
                        st.experimental_rerun()

            st.markdown("---")

            # ------------------------------------------
            # Candidatos aplicados
            # ------------------------------------------
            st.markdown("### 👤 Candidatos que han aplicado")

            apps_data = fetch_job_applications(job_id)
            applications = (apps_data or {}).get("applications") or []

            if not applications:
                st.info("Aún no hay candidatos aplicados a esta vacante.")
            else:
                for app in applications:
                    candidate_id = app.get("candidate_id")
                    candidate_name = app.get("candidate_name") or "Candidato sin nombre"
                    candidate_email = app.get("candidate_email") or "Sin email"
                    applied_at = app.get("applied_at") or "Fecha no disponible"
                    status_app = app.get("status") or "applied"

                    # ---------------- MATCHING REAL ----------------
                    scores = fetch_matching_scores(candidate_id, job_id) if candidate_id else None

                    def _safe_score(v, default=None):
                        return v if isinstance(v, (int, float)) else default

                    if scores:
                        global_fit = _safe_score(scores.get("global_fit"), 0)
                        skills_fit = _safe_score(scores.get("skills_fit"), 0)
                        values_fit = _safe_score(scores.get("values_fit"), None)
                        team_fit = _safe_score(scores.get("team_fit"), None)
                    else:
                        global_fit = 0
                        skills_fit = 0
                        values_fit = None
                        team_fit = None

                    # ---------------- PERFIL DEL CANDIDATO ----------------
                    candidate_profile = fetch_candidate_profile(candidate_id) if candidate_id else None
                    headline = candidate_profile.get("headline") if candidate_profile else None
                    location_cand = candidate_profile.get("location") if candidate_profile else None
                    years_exp = candidate_profile.get("years_experience") if candidate_profile else None

                    a_col1, a_col2, a_col3, a_col4 = st.columns([3,2,2,2])

                    with a_col1:
                        st.markdown(f"**{candidate_name}**")
                        st.caption(candidate_email)
                        if headline:
                            st.caption(f"💼 {headline}")
                        if location_cand:
                            st.caption(f"📍 {location_cand}")

                    with a_col2:
                        st.markdown(f"Estado: `{status_app}`")
                        st.caption(f"Aplicó: {applied_at}")
                        st.metric("Encaje global", f"{global_fit:.0f} / 100")

                    with a_col3:
                        st.markdown("**Skills fit**")
                        st.progress(int(skills_fit or 0))
                        st.caption(f"{skills_fit:.0f} / 100")

                    with a_col4:
                        st.markdown("**Valores / Team**")
                        st.text(f"Valores: {values_fit:.0f}/100" if values_fit is not None else "Valores: N/A")
                        st.text(f"Equipo:  {team_fit:.0f}/100" if team_fit is not None else "Equipo:  N/A")

                    # --------------- DETALLE (YA SIN EXPANDER ANIDADO) ---------------
                    st.markdown("#### 🔎 Detalle del candidato")
                    if candidate_profile:
                        st.write(f"Nombre completo: **{candidate_profile.get('full_name') or candidate_name}**")
                        if years_exp is not None:
                            st.write(f"**Años de experiencia:** {years_exp}")
                        if candidate_profile.get("current_role"):
                            st.write(f"**Rol actual:** {candidate_profile['current_role']}")
                        if candidate_profile.get("skills"):
                            st.markdown("**Skills principales:**")
                            skills = candidate_profile["skills"]
                            if isinstance(skills, list):
                                st.write(", ".join(skills))
                            else:
                                st.write(skills)
                    else:
                        st.info("No se pudo cargar el detalle del candidato.")

                    st.markdown("---")
                    st.markdown("**Detalle de matching:**")
                    st.write(f"- Encaje global: {global_fit:.0f}/100")
                    st.write(f"- Skills fit: {skills_fit:.0f}/100")
                    st.write(f"- Valores: {values_fit:.0f}/100" if values_fit is not None else "- Valores: N/A")
                    st.write(f"- Team fit: {team_fit:.0f}/100" if team_fit is not None else "- Team fit: N/A")

                    # Botón seleccionar
                    select_key = f"select_app_{job_id}_{app['application_id']}"
                    if st.button("✅ Seleccionar y enviar email", key=select_key):
                        res = select_application_backend(job_id, app["application_id"])
                        if res:
                            st.success("Candidato seleccionado y email enviado.")
                            st.session_state["refresh_company_jobs"] = True
                            st.experimental_rerun()

                    st.markdown("---")

            st.markdown("---")

            # ------------------------------------------
            # Edición de la vacante
            # ------------------------------------------
            st.markdown("### ✏️ Editar detalles de la vacante")

            with st.form(f"edit_job_form_{job_id}"):
                e_col1, e_col2 = st.columns(2)

                with e_col1:
                    new_title = st.text_input("Título del puesto", value=title)
                    new_location = st.text_input("Ubicación / modalidad", value=location)
                    new_department = st.text_input("Departamento / área", value=department)

                with e_col2:
                    new_contract_type = st.text_input("Tipo de contrato", value=job.get("contract_type", ""))
                    new_salary_range = st.text_input("Rango salarial", value=job.get("salary_range", ""))
                    new_seniority = st.selectbox(
                        "Seniority objetivo",
                        ["No especificado", "Junior", "Mid", "Senior", "Lead"],
                        index=["No especificado", "Junior", "Mid", "Senior", "Lead"]
                        .index(job.get("seniority", "No especificado"))
                        if job.get("seniority") in ["No especificado", "Junior", "Mid", "Senior", "Lead"]
                        else 0,
                    )

                new_status = st.selectbox(
                    "Estado de la vacante",
                    ["open", "closed", "paused"],
                    index=["open", "closed", "paused"].index(status) if status in ["open", "closed", "paused"] else 0,
                )

                submitted_edit = st.form_submit_button("Guardar cambios")

            if submitted_edit:
                payload = {
                    "title": new_title,
                    "location": new_location,
                    "department": new_department,
                    "contract_type": new_contract_type,
                    "salary_range": new_salary_range,
                    "seniority": new_seniority,
                    "status": new_status,
                }

                with st.spinner("Actualizando la vacante..."):
                    res = update_job_backend(job_id, payload)

                if res:
                    st.success("Vacante actualizada correctamente.")
                    st.session_state["refresh_company_jobs"] = True
                    st.experimental_rerun()


# -------------------------
# Render principal de la página
# -------------------------
def render():
    company_id = ensure_company_id()
    if not company_id:
        st.stop()

    tab_create, tab_manage = st.tabs(["➕ Crear vacante", "📊 Gestionar vacantes"])

    with tab_create:
        render_create_job_tab(company_id)

    with tab_manage:
        render_manage_jobs_tab(company_id)
