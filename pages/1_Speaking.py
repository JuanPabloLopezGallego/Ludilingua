import streamlit as st
from streamlit_mic_recorder import speech_to_text
from utils import inicializar_sesion, actualizar_puntaje, mostrar_puntaje, reproducir_feedback
import random

st.set_page_config(page_title="Speaking Practice", page_icon="🎤", layout="centered")
inicializar_sesion()

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    h1, h2, p {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎤 Práctica de Pronunciación")

# Lista de palabras (puedes ampliarla)
palabras = ["apple", "banana", "elephant", "computer", "beautiful", "language"]
if "palabra_actual" not in st.session_state:
    st.session_state.palabra_actual = random.choice(palabras)

palabra = st.session_state.palabra_actual
st.markdown(f"### Pronuncia la siguiente palabra:")
st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{palabra}</h1>", unsafe_allow_html=True)

mostrar_puntaje()

# Reconocimiento de voz
texto_reconocido = speech_to_text(
    language='en',
    start_prompt="🎙️ Grabar",
    stop_prompt="⏹️ Detener",
    just_once=True,
    use_container_width=True,
    key="speech"
)

if texto_reconocido:
    st.write(f"Has dicho: **{texto_reconocido}**")
    acierto = texto_reconocido.lower().strip() == palabra.lower()
    mensaje = actualizar_puntaje(acierto)
    reproducir_feedback(acierto)
    if acierto:
        st.success(mensaje)
        if st.button("Siguiente palabra ➡️"):
            st.session_state.palabra_actual = random.choice(palabras)
            st.rerun()
    else:
        st.error(mensaje)
        st.write(f"Intenta de nuevo. La palabra correcta es: **{palabra}**")
