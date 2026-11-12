import streamlit as st
from gtts import gTTS
from io import BytesIO
import random
from utils import inicializar_sesion, actualizar_puntaje, mostrar_puntaje, reproducir_feedback

st.set_page_config(page_title="Listening Practice", page_icon="🎧", layout="centered")
inicializar_sesion()

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    h1, h2, p {
        color: #0a2e5c !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎧 Escucha y Escribe")

# Lista de palabras con audio
palabras_audio = ["cat", "dog", "house", "car", "tree", "sun"]
if "palabra_audio" not in st.session_state:
    st.session_state.palabra_audio = random.choice(palabras_audio)

palabra = st.session_state.palabra_audio

# Generar audio con gTTS
tts = gTTS(text=palabra, lang='en')
audio_bytes = BytesIO()
tts.write_to_fp(audio_bytes)
audio_bytes.seek(0)

st.markdown("### Escucha la palabra y escríbela:")
st.audio(audio_bytes, format="audio/mp3")

mostrar_puntaje()

respuesta = st.text_input("Escribe la palabra que escuchaste:", key="input_listening")

if st.button("Comprobar ✅"):
    if respuesta:
        acierto = respuesta.lower().strip() == palabra.lower()
        mensaje = actualizar_puntaje(acierto)
        reproducir_feedback(acierto)
        if acierto:
            st.success(mensaje)
            if st.button("Siguiente palabra ➡️"):
                st.session_state.palabra_audio = random.choice(palabras_audio)
                st.rerun()
        else:
            st.error(mensaje)
            st.write(f"La palabra correcta era: **{palabra}**")
    else:
        st.warning("Por favor, escribe una palabra.")
