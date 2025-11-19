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


def ensure_candidate_id():
    """
    Reutiliza la lógica de profile.py:
    - Si ya tenemos candidate_id en sesión, lo devuelve.
    - Si no, lo crea en /candidates/create a partir del email.
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


def call_hr_copilot_audio(candidate_id, audio_files_bytes: list):
    """
    Llama al endpoint de audio del HR Copilot.

    Args:
        candidate_id: ID del candidato
        audio_files_bytes: Lista de bytes de archivos de audio

    Returns:
        dict con análisis o None si falla
    """
    try:
        # Preparar archivos para multipart/form-data
        files = []
        for i, audio_bytes in enumerate(audio_files_bytes):
            files.append(
                ('audio_files', (f'answer_{i}.wav', audio_bytes, 'audio/wav'))
            )

        # Datos adicionales
        data = {
            'candidate_id': candidate_id,
            'language': 'es'
        }

        resp = requests.post(
            f"{BACKEND_URL}/copilot/process_call_audio",
            files=files,
            data=data,
            timeout=120  # 2 minutos para transcripción + análisis
        )

        if resp.status_code != 200:
            st.error(f"Error del servidor: {resp.status_code}")
            try:
                st.json(resp.json())
            except:
                st.write(resp.text)
            return None

        return resp.json()

    except Exception as e:
        st.error(f"Error al procesar audio: {e}")
        return None


def call_hr_copilot(candidate_id, answers: list[str], questions: list[str] | None = None):
    """
    Llama al endpoint del HR Copilot.
    Contrato real backend (POST /copilot/process_call):
      {
        "candidate_id": int,
        "answers": ["respuesta1", "respuesta2", ...],
        "questions": ["pregunta1", "pregunta2", ...]  # opcional
      }
    """
    payload = {
        "candidate_id": candidate_id,
        "answers": answers,
    }
    if questions:
        payload["questions"] = questions

    try:
        resp = requests.post(
            f"{BACKEND_URL}/copilot/process_call",
            json=payload,
            timeout=60,
        )
    except Exception as e:
        st.error(f"Error al llamar al HR Copilot: {e}")
        return None

    if resp.status_code != 200:
        st.error(f"El HR Copilot devolvió un error. Código: {resp.status_code}")
        try:
            st.json(resp.json())
        except Exception:
            st.write(resp.text)
        return None

    return resp.json()


# -------------------------
# Bloque de transparencia / honestidad
# -------------------------
def render_honesty_message():
    st.markdown("### 💬 Antes de empezar: sé tú mismo/a")
    st.info(
        "Esta llamada con la IA está diseñada para conocerte mejor a nivel de **motivaciones**, "
        "**valores**, **soft skills** y **forma de trabajar en equipo**.\n\n"
        "**No es un examen.** Lo que más se valora es que te muestres tal y como eres.\n\n"
        "Nuestro algoritmo está entrenado para detectar patrones de **exageración o respuestas poco naturales**. "
        "Cuando esto ocurre, el resultado puede verse **empeorado** y no reflejar bien tu verdadero potencial.\n\n"
        "Responder con sinceridad te ayuda a obtener un perfil más preciso y a encontrar vacantes "
        "donde realmente puedas encajar y sentirte a gusto. 💜"
    )


# -------------------------
# Render principal de la página
# -------------------------
def render():
    st.markdown("## 🎙️ Llamada IA – HR Copilot")
    st.caption(
        "Aquí puedes realizar una llamada asíncrona con nuestra IA de RRHH. "
        "Tus respuestas completan tu perfil para que las vacantes recomendadas y el encaje de equipo "
        "sean lo más fieles posible a quién eres de verdad."
    )

    candidate_id = ensure_candidate_id()
    if not candidate_id:
        st.stop()

    # -----------------------------------------
    # GRABACIÓN DE VOZ
    # -----------------------------------------
    st.markdown("### 🎙️ Opción 1: Responder por Voz")
    st.caption("Graba tus respuestas hablando. El sistema las transcribirá automáticamente con Whisper.")

    use_audio = st.checkbox("✅ Quiero responder por voz", key="use_audio_checkbox")

    if use_audio:
        st.info("🎤 **Cómo funciona:**\n"
                "1. Permite acceso al micrófono cuando lo solicite el navegador\n"
                "2. Habla tu respuesta de forma natural para cada pregunta\n"
                "3. Graba al menos 2 respuestas\n"
                "4. Envía todas las grabaciones para análisis")

        # Inicializar almacenamiento de audios
        if "audio_recordings" not in st.session_state:
            st.session_state.audio_recordings = {}

        default_questions = [
            "¿Qué te motiva profesionalmente en este momento?",
            "Descríbeme una situación en la que hayas trabajado en equipo y te hayas sentido muy a gusto.",
            "¿Qué tipo de cultura de empresa sientes como más alineada contigo?",
            "Cuéntame un logro profesional del que estés especialmente orgulloso/a.",
            "¿Qué tipo de tareas o entornos te generan más estrés o frustración?",
            "¿Cómo te gustaría que fuera tu manager ideal?",
        ]

        st.markdown("#### 🎙️ Graba tus respuestas")

        # Usar componente experimental de audio de Streamlit
        for i, question in enumerate(default_questions):
            with st.expander(f"📝 Pregunta {i+1}: {question}", expanded=(i==0)):
                st.write(f"**{question}**")

                # Usar st.audio_input (disponible en Streamlit 1.28+)
                try:
                    audio_bytes = st.audio_input(
                        f"Graba tu respuesta {i+1}",
                        key=f"audio_input_{i}"
                    )

                    if audio_bytes:
                        # Leer los bytes del audio
                        audio_data = audio_bytes.read()
                        st.session_state.audio_recordings[i] = audio_data
                        st.success(f"✅ Respuesta {i+1} grabada ({len(audio_data)} bytes)")

                        # Mostrar botón para borrar
                        if st.button(f"🗑️ Borrar grabación {i+1}", key=f"delete_{i}"):
                            if i in st.session_state.audio_recordings:
                                del st.session_state.audio_recordings[i]
                                st.rerun()
                    elif i in st.session_state.audio_recordings:
                        st.info(f"✅ Respuesta {i+1} ya grabada")
                        if st.button(f"🗑️ Borrar grabación {i+1}", key=f"delete_stored_{i}"):
                            del st.session_state.audio_recordings[i]
                            st.rerun()

                except AttributeError:
                    # Fallback si audio_input no está disponible
                    st.warning("🎙️ La grabación de audio requiere Streamlit 1.28 o superior.")
                    st.info("💡 **Alternativa:** Usa la opción de texto abajo")
                    break

        # Botón de envío
        if len(st.session_state.audio_recordings) >= 2:
            st.markdown("---")
            st.success(f"✅ {len(st.session_state.audio_recordings)} respuestas grabadas")

            honest_check_audio = st.checkbox(
                "Confirmo que he respondido de forma sincera",
                key="honest_audio"
            )

            if st.button("🚀 Enviar Grabaciones para Análisis", use_container_width=True, type="primary"):
                if not honest_check_audio:
                    st.error("Por favor, marca la casilla de confirmación.")
                else:
                    with st.spinner("🎙️ Transcribiendo audio con Whisper y analizando con IA..."):
                        # Preparar archivos de audio
                        audio_files = []
                        for idx in sorted(st.session_state.audio_recordings.keys()):
                            audio_files.append(st.session_state.audio_recordings[idx])

                        # Llamar al endpoint de audio
                        result = call_hr_copilot_audio(candidate_id, audio_files)

                    if result:
                        st.balloons()
                        st.success("✅ ¡Análisis completado! Tu perfil se ha actualizado.")
                        st.session_state["hr_copilot_last_result"] = result

                        # Mostrar transcripciones si están disponibles
                        if "transcriptions" in result:
                            with st.expander("📝 Ver transcripciones de tus respuestas"):
                                for i, transcription in enumerate(result["transcriptions"], 1):
                                    st.markdown(f"**Respuesta {i}:**")
                                    st.write(transcription)
                                    st.markdown("---")

                        st.info("💡 Desplázate hacia abajo para ver el análisis completo.")
                        # Limpiar grabaciones
                        st.session_state.audio_recordings = {}
                    else:
                        st.error("❌ Hubo un problema al procesar el audio.")
        elif len(st.session_state.audio_recordings) > 0:
            st.warning(f"⚠️ Has grabado {len(st.session_state.audio_recordings)} respuesta(s). Graba al menos 2 para continuar.")

    st.markdown("---")
    st.markdown("### 📝 Opción 2: Responder por Texto")
    st.caption("Escribe tus respuestas en los campos de texto.")

    # Explicación de qué va a completarse en el perfil
    with st.expander("ℹ️ ¿Qué va a completar esta llamada en tu perfil?"):
        st.markdown(
            """
La IA utilizará tus respuestas para construir y actualizar estos apartados de tu perfil:

- 💡 **Motivaciones**: qué te mueve y qué buscas en tu trabajo.
- 🌱 **Valores detectados**: qué principios son importantes para ti.
- 🤝 **Soft skills**: cómo te relacionas, comunicas y trabajas con otras personas.
- 🏆 **Experiencia clave**: momentos de tu trayectoria que te definen.
- 🧩 **Preferencias de equipo**: qué tipo de entorno y compañeros encajan mejor contigo.
- 🧬 **Resumen psicológico-profesional**: una síntesis global para el matching con empresas.

Todo esto se muestra de forma transparente al final de la página para que sepas exactamente
cómo te está “viendo” el sistema.
"""
        )

    st.markdown("---")

    # -------------------------
    # Bloque de honestidad y refuerzo positivo
    # -------------------------
    render_honesty_message()

    st.markdown("### 🧠 Cuestionario para la IA")

    default_questions = [
        "¿Qué te motiva profesionalmente en este momento?",
        "Descríbeme una situación en la que hayas trabajado en equipo y te hayas sentido muy a gusto.",
        "¿Qué tipo de cultura de empresa sientes como más alineada contigo?",
        "Cuéntame un logro profesional del que estés especialmente orgulloso/a.",
        "¿Qué tipo de tareas o entornos te generan más estrés o frustración?",
        "¿Cómo te gustaría que fuera tu manager ideal?",
    ]

    with st.form("hr_copilot_form"):
        answers_pairs = []  # (pregunta, respuesta)
        for i, q in enumerate(default_questions):
            answer = st.text_area(
                f"{i+1}. {q}",
                key=f"q_{i}",
                height=80,
            )
            answers_pairs.append((q, answer))

        st.markdown("----")
        honest_check = st.checkbox(
            "Confirmo que responderé de forma sincera, sin exagerar, "
            "para que el resultado refleje quién soy realmente."
        )

        submitted = st.form_submit_button("Enviar respuestas a la IA")

    if submitted:
        if not honest_check:
            st.error(
                "Por favor, marca la casilla de confirmación. Queremos que el análisis sea justo contigo "
                "y refleje quién eres de verdad."
            )
            return

        # Validación mínima: al menos 2 respuestas no vacías
        non_empty_pairs = [(q, a) for (q, a) in answers_pairs if a and a.strip()]
        if len(non_empty_pairs) < 2:
            st.error("Responde al menos a un par de preguntas para que la IA pueda trabajar bien.")
            return

        questions = [q for (q, _) in non_empty_pairs]
        answers_only = [a.strip() for (_, a) in non_empty_pairs]

        with st.spinner("🤖 Analizando tus respuestas con el HR Copilot..."):
            result = call_hr_copilot(candidate_id, answers_only, questions)

        if result:
            st.balloons()
            st.success("✅ ¡Análisis completado! Tu perfil se ha actualizado con esta información.")
            st.session_state["hr_copilot_last_result"] = result
            st.info("💡 Desplázate hacia abajo para ver el análisis completo de tu perfil.")
        else:
            st.error("❌ Hubo un problema al procesar tus respuestas. Por favor, intenta de nuevo.")
            st.info("Si el problema persiste, verifica que el backend esté funcionando correctamente.")

    # -------------------------
    # Bloque de transparencia: mostrar TODO lo que completa el perfil
    # -------------------------
    result = st.session_state.get("hr_copilot_last_result")
    st.markdown("---")
    st.markdown("### 📂 Tu perfil tras la llamada IA")

    if result:
        st.caption(
            "Esta sección muestra de forma transparente cómo está utilizando el sistema tus respuestas "
            "para completar tu perfil."
        )

        # Tarjeta resumen
        st.markdown("#### 🧬 Resumen psicológico-profesional")
        resumen_psicologico = result.get("resumen_psicologico")
        if resumen_psicologico:
            st.write(resumen_psicologico)
        else:
            st.info("Aún no hay un resumen psicológico generado por la IA.")

        col1, col2 = st.columns(2)

        with col1:
            motivaciones = result.get("motivaciones")
            if motivaciones:
                st.markdown("#### 💡 Motivaciones")
                st.write(motivaciones)

            experiencia_clave = result.get("experiencia_clave")
            if experiencia_clave:
                st.markdown("#### 🏆 Experiencia clave")
                st.write(experiencia_clave)

        with col2:
            soft_skills = result.get("soft_skills")
            if soft_skills:
                st.markdown("#### 🤝 Soft skills detectadas")
                if isinstance(soft_skills, list):
                    st.write(", ".join(soft_skills))
                else:
                    st.write(soft_skills)

            preferencias_equipo = result.get("preferencias_equipo")
            if preferencias_equipo:
                st.markdown("#### 🧩 Preferencias de equipo")
                st.write(preferencias_equipo)

        valores = result.get("valores_detectados")
        if valores:
            st.markdown("#### 🌱 Valores detectados")
            if isinstance(valores, list):
                st.write(", ".join(valores))
            else:
                st.write(valores)

        with st.expander("Ver JSON completo devuelto por el HR Copilot (modo técnico)"):
            st.json(result)
    else:
        st.info(
            "Cuando completes la llamada IA, aquí verás de forma clara cómo se ha actualizado tu perfil "
            "con lo que la IA ha entendido de ti."
        )