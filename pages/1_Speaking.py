import streamlit as st
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from utils import (
    inicializar_sesion, actualizar_puntaje, mostrar_puntaje,
    publicar_feedback, obtener_ultimo_mensaje_boton, elegir_siguiente_item
)
import random

st.set_page_config(page_title="Speaking Practice", page_icon="🎤", layout="centered")

# Escucha eventos del botón de Wokwi sin perder mensajes gracias a la cola en utils.py
st_autorefresh(interval=1500, key="mqtt_refresh_speaking")

inicializar_sesion()

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    h1, h2, h3, p { color: #ffffff !important; }
    @keyframes pop { 0% { transform: scale(0.8); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
    .word-display { text-align: center; font-size: 82px; font-weight: bold; color: #fff; text-shadow: 2px 2px 8px rgba(0,0,0,0.3); animation: pop 0.4s ease-out; margin: 15px 0; }
</style>
""", unsafe_allow_html=True)

st.title("🎤 Práctica de Pronunciación")

palabras = ["apple", "banana", "elephant", "computer", "beautiful", "language"]

if "palabra_actual" not in st.session_state:
    st.session_state.palabra_actual = random.choice(palabras)
if "speaking_resultado" not in st.session_state:
    st.session_state.speaking_resultado = None

# Detectar botón físico de Wokwi
if obtener_ultimo_mensaje_boton() == "AVANZAR":
    st.session_state.palabra_actual = elegir_siguiente_item(palabras, st.session_state.palabra_actual)
    st.session_state.speaking_resultado = None
    st.toast("🔘 ¡Botón de Wokwi detectado! Nueva palabra cargada.", icon="🚀")

palabra = st.session_state.palabra_actual
mostrar_puntaje()

st.markdown("### Pronuncia la siguiente palabra:")
st.markdown(f"<div class='word-display'>{palabra}</div>", unsafe_allow_html=True)

texto_reconocido = speech_to_text(
    language='en',
    start_prompt="🎙️ Grabar pronunciación",
    stop_prompt="⏹️ Detener y evaluar",
    just_once=True,
    use_container_width=True,
    key=f"speech_{palabra}"
)

if texto_reconocido:
    limpio = texto_reconocido.lower().strip().rstrip(".,!?")
    acierto = (limpio == palabra.lower())
    mensaje = actualizar_puntaje(acierto)
    publicar_feedback(acierto)  # Dispara LED y melodía en Wokwi al instante
    st.session_state.speaking_resultado = (acierto, texto_reconocido, mensaje)

# Mostrar el último resultado de forma persistente aunque ocurra un autorefresh
if st.session_state.speaking_resultado:
    acierto, dicho, mensaje = st.session_state.speaking_resultado
    st.write(f"Has dicho: **{dicho}**")
    if acierto:
        st.success(mensaje)
    else:
        st.error(mensaje)
        st.info(f"💡 Intenta de nuevo o presiona el botón en Wokwi para saltar.")

if st.button("Siguiente palabra ➡️", use_container_width=True):
    st.session_state.palabra_actual = elegir_siguiente_item(palabras, palabra)
    st.session_state.speaking_resultado = None
    st.rerun()
