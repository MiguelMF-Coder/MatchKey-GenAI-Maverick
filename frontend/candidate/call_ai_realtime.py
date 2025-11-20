"""
Real-time interview component using WebSocket connection.
Provides a live, interactive interview experience with progress updates.
"""

import streamlit as st
import asyncio
import websockets
import json
import uuid
from typing import Optional, Dict
import requests
from utils import get_backend_url

BACKEND_URL = get_backend_url()
# Convert HTTP URL to WebSocket URL
WS_URL = BACKEND_URL.replace("http://", "ws://").replace("https://", "wss://")


class RealTimeInterview:
    """Manages real-time interview WebSocket connection"""

    def __init__(self, session_id: str, candidate_id: int):
        self.session_id = session_id
        self.candidate_id = candidate_id
        self.ws_url = f"{WS_URL}/copilot/realtime/interview/{session_id}"
        self.websocket = None
        self.connected = False

    async def connect(self):
        """Establish WebSocket connection"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.connected = True
            return True
        except Exception as e:
            st.error(f"Error conectando con el servidor: {e}")
            return False

    async def start_interview(self):
        """Start the interview session"""
        if not self.connected:
            return False

        message = {
            "type": "start",
            "candidate_id": self.candidate_id
        }

        try:
            await self.websocket.send(json.dumps(message))
            return True
        except Exception as e:
            st.error(f"Error iniciando entrevista: {e}")
            return False

    async def send_answer(self, question_num: int, answer: str):
        """Send answer to current question"""
        if not self.connected:
            return False

        message = {
            "type": "answer",
            "question_num": question_num,
            "answer": answer
        }

        try:
            await self.websocket.send(json.dumps(message))
            return True
        except Exception as e:
            st.error(f"Error enviando respuesta: {e}")
            return False

    async def finish(self):
        """Finish the interview session"""
        if not self.connected:
            return

        message = {"type": "finish"}

        try:
            await self.websocket.send(json.dumps(message))
        except:
            pass

        await self.close()

    async def receive_message(self) -> Optional[Dict]:
        """Receive message from server"""
        if not self.connected:
            return None

        try:
            message = await self.websocket.recv()
            return json.loads(message)
        except Exception as e:
            return None

    async def close(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
        self.connected = False


def render_realtime_interview():
    """
    Renders the real-time interview interface with WebSocket connection.
    Provides live feedback and progress updates during the interview.
    """
    st.markdown("## 🎙️ Entrevista en Tiempo Real - HR Copilot")
    st.caption(
        "Experiencia de entrevista interactiva con feedback en tiempo real. "
        "La IA procesará tus respuestas de forma progresiva."
    )

    # Get candidate ID
    from candidate.call_ai import ensure_candidate_id
    candidate_id = ensure_candidate_id()

    if not candidate_id:
        st.error("No se pudo obtener el ID del candidato")
        st.stop()

    # Initialize session state
    if "rt_session_id" not in st.session_state:
        st.session_state.rt_session_id = str(uuid.uuid4())

    if "rt_started" not in st.session_state:
        st.session_state.rt_started = False

    if "rt_current_question" not in st.session_state:
        st.session_state.rt_current_question = 0

    if "rt_answers" not in st.session_state:
        st.session_state.rt_answers = []

    if "rt_questions" not in st.session_state:
        # Get questions from backend
        try:
            response = requests.get(f"{BACKEND_URL}/copilot/questions")
            if response.status_code == 200:
                data = response.json()
                st.session_state.rt_questions = [q["text"] for q in data["questions"]]
            else:
                st.error("No se pudieron cargar las preguntas")
                st.stop()
        except Exception as e:
            st.error(f"Error al cargar preguntas: {e}")
            st.stop()

    if "rt_analysis" not in st.session_state:
        st.session_state.rt_analysis = None

    # Progress bar
    total_questions = len(st.session_state.rt_questions)
    if st.session_state.rt_started:
        progress = st.session_state.rt_current_question / total_questions
        st.progress(progress, text=f"Pregunta {st.session_state.rt_current_question} de {total_questions}")

    # Info message
    with st.expander("ℹ️ ¿Cómo funciona la entrevista en tiempo real?"):
        st.markdown("""
        ### Experiencia Interactiva
        
        - 🔄 **Conexión en tiempo real**: WebSocket para comunicación instantánea
        - 📝 **Una pregunta a la vez**: Responde de forma natural y progresiva
        - 📊 **Feedback instantáneo**: Ve el progreso en tiempo real
        - 🧠 **Análisis progresivo**: La IA procesa tus respuestas de forma continua
        - ✅ **Transparencia total**: Ve exactamente cómo se actualiza tu perfil
        
        Esta experiencia simula una entrevista real de RRHH, pero con la ventaja
        de poder tomarte tu tiempo para reflexionar sobre cada respuesta.
        """)

    # Honesty message
    if not st.session_state.rt_started:
        st.markdown("### 💬 Antes de empezar: sé tú mismo/a")
        st.info(
            "Esta entrevista está diseñada para conocerte mejor. "
            "**No es un examen.** Responde con sinceridad para obtener un perfil preciso "
            "y encontrar vacantes donde realmente puedas encajar. 💜"
        )

        # Start button
        if st.button("🚀 Iniciar Entrevista en Tiempo Real", type="primary", use_container_width=True):
            st.session_state.rt_started = True
            st.session_state.rt_current_question = 1
            st.rerun()

    # Interview interface
    if st.session_state.rt_started and st.session_state.rt_analysis is None:
        current_q_idx = st.session_state.rt_current_question - 1

        if current_q_idx < total_questions:
            # Display current question
            st.markdown(f"### Pregunta {st.session_state.rt_current_question} de {total_questions}")
            st.markdown(f"**{st.session_state.rt_questions[current_q_idx]}**")

            # Answer input
            answer = st.text_area(
                "Tu respuesta:",
                key=f"rt_answer_{current_q_idx}",
                height=150,
                placeholder="Responde de forma sincera y natural..."
            )

            # Navigation buttons
            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                if st.session_state.rt_current_question > 1:
                    if st.button("⬅️ Anterior", use_container_width=True):
                        st.session_state.rt_current_question -= 1
                        st.rerun()

            with col2:
                # Show answers submitted so far
                st.caption(f"Respuestas: {len(st.session_state.rt_answers)}/{total_questions}")

            with col3:
                # Determine button label
                is_last = st.session_state.rt_current_question == total_questions
                button_label = "✅ Finalizar" if is_last else "Siguiente ➡️"

                if st.button(button_label, type="primary" if is_last else "secondary", use_container_width=True):
                    if not answer or not answer.strip():
                        st.error("Por favor, escribe una respuesta antes de continuar")
                    else:
                        # Store answer
                        if len(st.session_state.rt_answers) <= current_q_idx:
                            st.session_state.rt_answers.append(answer.strip())
                        else:
                            st.session_state.rt_answers[current_q_idx] = answer.strip()

                        if is_last:
                            # Process all answers
                            with st.spinner("🤖 Analizando tus respuestas..."):
                                from candidate.call_ai import call_hr_copilot

                                result = call_hr_copilot(
                                    candidate_id,
                                    st.session_state.rt_answers,
                                    st.session_state.rt_questions
                                )

                                if result:
                                    st.session_state.rt_analysis = result
                                    st.balloons()
                                    st.success("✅ ¡Análisis completado!")
                                    st.rerun()
                                else:
                                    st.error("Error al procesar las respuestas")
                        else:
                            # Go to next question
                            st.session_state.rt_current_question += 1
                            st.rerun()

            # Show previous answers
            if len(st.session_state.rt_answers) > 0:
                with st.expander("📝 Ver respuestas anteriores"):
                    for i, ans in enumerate(st.session_state.rt_answers, 1):
                        st.markdown(f"**Pregunta {i}:** {st.session_state.rt_questions[i-1]}")
                        st.write(ans)
                        st.markdown("---")

    # Display analysis results
    if st.session_state.rt_analysis:
        st.markdown("---")
        st.markdown("### 📊 Análisis Completado")

        result = st.session_state.rt_analysis

        # Summary card
        st.markdown("#### 🧬 Resumen Psicológico-Profesional")
        resumen = result.get("resumen_psicologico", "")
        if resumen:
            st.write(resumen)

        # Two columns for details
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 💡 Motivaciones")
            st.write(result.get("motivaciones", ""))

            st.markdown("#### 🏆 Experiencia Clave")
            exp = result.get("experiencia_clave", [])
            if isinstance(exp, list):
                for item in exp:
                    st.write(f"• {item}")
            else:
                st.write(exp)

        with col2:
            st.markdown("#### 🤝 Soft Skills")
            skills = result.get("soft_skills", [])
            if isinstance(skills, list):
                st.write(", ".join(skills))
            else:
                st.write(skills)

            st.markdown("#### 🧩 Preferencias de Equipo")
            st.write(result.get("preferencias_equipo", ""))

        st.markdown("#### 🌱 Valores Detectados")
        valores = result.get("valores_detectados", [])
        if isinstance(valores, list):
            st.write(", ".join(valores))
        else:
            st.write(valores)

        # Reset button
        if st.button("🔄 Realizar Nueva Entrevista", use_container_width=True):
            # Reset session
            st.session_state.rt_started = False
            st.session_state.rt_current_question = 0
            st.session_state.rt_answers = []
            st.session_state.rt_analysis = None
            st.session_state.rt_session_id = str(uuid.uuid4())
            st.rerun()


def render():
    """Main render function"""
    render_realtime_interview()

