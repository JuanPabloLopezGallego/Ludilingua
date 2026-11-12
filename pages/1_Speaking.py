import streamlit as st
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from utils import (inicializar_sesion, actualizar_puntaje, mostrar_puntaje, 
                   publicar_feedback, obtener_ultimo_mensaje_boton)
import random

st.set_page_config(page_title="Speaking Practice", page_icon="🎤", layout="centered")

# Refresco para MQTT (permite que el botón de Wokwi avance en cualquier momento)
st_autorefresh(interval=1000, key="mqtt_refresh_speaking")

inicializar_sesion()

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    h1, h2, h3, p { color: #ffffff !important; }
    @keyframes pop { 0% { transform: scale(0.8); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
    .word-display { text-align: center; font-size: 90px; font-weight: bold; color: #fff; text-shadow: 2px 2px 8px rgba(0,0,0,0.3); animation: pop 0.5s ease-out; }
</style>
""", unsafe_allow_html=True)

st.title("🎤 Práctica de Pronunciación")

# Detectar botón de Wokwi
mensaje_boton = obtener_ultimo_mensaje_boton()
if mensaje_boton == "AVANZAR":
    if "palabra_actual" in st.session_state:
        del st.session_state.palabra_actual
    st.toast("🔘 ¡Botón de Wokwi presionado! Siguiente palabra.")

palabras = ["apple", "banana", "elephant", "computer", "beautiful", "language"]
if "palabra_actual" not in st.session_state:
    st.session_state.palabra_actual = random.choice(palabras)

palabra = st.session_state.palabra_actual
st.markdown("### Pronuncia la siguiente palabra:")
st.markdown(f"<div class='word-display'>{palabra}</div>", unsafe_allow_html=True)

mostrar_puntaje()

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
    publicar_feedback(acierto)
    
    if acierto:
        st.success(mensaje)
        if st.button("Siguiente palabra ➡️"):
            st.session_state.palabra_actual = random.choice(palabras)
            st.rerun()
    else:
        st.error(mensaje)
        st.write(f"Intenta de nuevo. La palabra correcta es: **{palabra}**")
