import streamlit as st
from gtts import gTTS
from io import BytesIO
from streamlit_autorefresh import st_autorefresh
import random
from utils import (
    inicializar_sesion, actualizar_puntaje, mostrar_puntaje,
    publicar_feedback, obtener_ultimo_mensaje_boton, elegir_siguiente_item
)

st.set_page_config(page_title="Listening Practice", page_icon="🎧", layout="centered")

st_autorefresh(interval=1500, key="mqtt_refresh_listening")

inicializar_sesion()

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    h1, h2, h3, p { color: #0a2e5c !important; }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.08); } 100% { transform: scale(1); } }
    .audio-icon { text-align: center; font-size: 75px; animation: pulse 2s infinite; }
</style>
""", unsafe_allow_html=True)

st.title("🎧 Escucha y Escribe")

palabras_audio = ["cat", "dog", "house", "car", "tree", "sun"]

if "palabra_audio" not in st.session_state:
    st.session_state.palabra_audio = random.choice(palabras_audio)
if "listening_step" not in st.session_state:
    st.session_state.listening_step = 0
if "listening_resultado" not in st.session_state:
    st.session_state.listening_resultado = None


@st.cache_data(show_spinner=False)
def generar_audio_mp3(texto: str) -> bytes:
    tts = gTTS(text=texto, lang='en')
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    return audio_bytes.getvalue()


def avanzar_palabra_audio():
    st.session_state.palabra_audio = elegir_siguiente_item(palabras_audio, st.session_state.palabra_audio)
    st.session_state.listening_step += 1  # Limpia el text_input automáticamente
    st.session_state.listening_resultado = None


# Detectar botón físico de Wokwi
if obtener_ultimo_mensaje_boton() == "AVANZAR":
    avanzar_palabra_audio()
    st.toast("🔘 ¡Botón de Wokwi presionado! Nuevo audio listo.", icon="🎧")

palabra = st.session_state.palabra_audio
mostrar_puntaje()

st.markdown("<div class='audio-icon'>🔊</div>", unsafe_allow_html=True)
st.markdown("### Escucha la palabra y escríbela:")
st.audio(generar_audio_mp3(palabra), format="audio/mp3")

with st.form(key=f"form_listening_{st.session_state.listening_step}"):
    respuesta = st.text_input("Escribe la palabra que escuchaste (y presiona Enter o Comprobar):")
    comprobar = st.form_submit_button("Comprobar ✅", use_container_width=True)

if comprobar:
    if respuesta.strip():
        acierto = respuesta.lower().strip() == palabra.lower()
        mensaje = actualizar_puntaje(acierto)
        publicar_feedback(acierto)  # Suena el buzzer y enciende LED en Wokwi
        st.session_state.listening_resultado = (acierto, mensaje, palabra)
    else:
        st.warning("Por favor, escribe una palabra antes de comprobar.")

# Resultado fuera del botón comprobar (sin botones anidados)
if st.session_state.listening_resultado:
    acierto, mensaje, palabra_evaluada = st.session_state.listening_resultado
    if acierto:
        st.success(mensaje)
    else:
        st.error(mensaje)
        st.info(f"La palabra correcta era: **{palabra_evaluada}**")

if st.button("Siguiente palabra ➡️", use_container_width=True):
    avanzar_palabra_audio()
    st.rerun()
