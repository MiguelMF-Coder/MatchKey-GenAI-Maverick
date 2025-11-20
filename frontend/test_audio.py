"""
Script de prueba para verificar la disponibilidad de st.audio_input
"""
import streamlit as st

st.title("🎙️ Test de Audio Input")

st.write(f"**Versión de Streamlit:** {st.__version__}")

# Verificar si audio_input está disponible
if hasattr(st, 'audio_input'):
    st.success("✅ st.audio_input está disponible!")

    st.markdown("---")
    st.markdown("### Prueba de grabación")

    audio_bytes = st.audio_input("Graba un mensaje de prueba")

    if audio_bytes:
        st.success("✅ Audio grabado exitosamente!")
        audio_data = audio_bytes.read()
        st.write(f"Tamaño del audio: {len(audio_data)} bytes")

        # Reproducir el audio grabado
        st.audio(audio_data)
else:
    st.error("❌ st.audio_input NO está disponible")
    st.warning(f"Versión actual: {st.__version__}")
    st.info("Se requiere Streamlit >= 1.28.0")

    # Verificar otros atributos relacionados
    st.markdown("### Atributos de Streamlit disponibles:")
    audio_attrs = [attr for attr in dir(st) if 'audio' in attr.lower()]
    st.write(audio_attrs)

