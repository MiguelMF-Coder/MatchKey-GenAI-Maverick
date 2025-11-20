"""
Script de prueba para verificar la disponibilidad de st.audio_input
Usado para testing de grabación de audio que se transcribe con Groq Whisper API
"""
import streamlit as st

st.title("🎙️ Test de Audio Input - Groq Whisper Integration")

st.write(f"**Versión de Streamlit:** {st.__version__}")

st.info(
    "Este test verifica que puedes grabar audio localmente. "
    "La transcripción se hace con **Groq Whisper API** en el backend."
)

# Verificar si audio_input está disponible
if hasattr(st, 'audio_input'):
    st.success("✅ st.audio_input está disponible!")

    st.markdown("---")
    st.markdown("### Prueba de grabación")

    st.caption("Graba un mensaje de prueba. Se guardará localmente y luego se enviará al backend para transcripción con Groq.")

    audio_bytes = st.audio_input("Graba un mensaje de prueba")

    if audio_bytes:
        st.success("✅ Audio grabado exitosamente!")
        audio_data = audio_bytes.read()
        st.write(f"Tamaño del audio: {len(audio_data)} bytes")

        # Reproducir el audio grabado
        st.audio(audio_data)

        st.info("Este audio se enviaría al backend para transcripción con Groq Whisper API (whisper-large-v3-turbo)")
else:
    st.error("❌ st.audio_input NO está disponible")
    st.warning(f"Versión actual: {st.__version__}")
    st.info(
        "Se requiere Streamlit >= 1.39.0 para la grabación de audio.\n\n"
        "**Actualizar:**\n"
        "```bash\n"
        "pip install --upgrade streamlit>=1.39.0\n"
        "```"
    )

    # Verificar otros atributos relacionados
    st.markdown("### Atributos de Streamlit disponibles:")
    audio_attrs = [attr for attr in dir(st) if 'audio' in attr.lower()]
    st.write(audio_attrs)

