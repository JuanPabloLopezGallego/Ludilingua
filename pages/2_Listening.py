import streamlit as st
from gtts import gTTS
from io import BytesIO
from streamlit_autorefresh import st_autorefresh
import random
from utils import (inicializar_sesion, actualizar_puntaje, mostrar_puntaje,
                   publicar_feedback, reproducir_feedback, boton_avanzar_presionado)

st.set_page_config(page_title="Listening Practice", page_icon="🎧", layout="centered")
st_autorefresh(interval=3000, key="mqtt_refresh_listening")
inicializar_sesion()

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    h1, h2, h3, p { color: #0a2e5c !important; }
    .audio-icon { text-align: center; font-size: 80px; }
</style>
""", unsafe_allow_html=True)

st.title("🎧 Escucha y Escribe")

@st.cache_data(show_spinner=False)
def obtener_audio(palabra: str):
    try:
        tts = gTTS(text=palabra, lang='en')
        buf = BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        print(f"Error gTTS: {e}")
        return None

def nueva_palabra_listening():
    actual = st.session_state.palabra_audio
    opciones = [p for p in palabras_audio if p != actual]
    st.session_state.palabra_audio = random.choice(opciones)
    st.session_state.listening_round += 1
    st.session_state.listening_estado = "esperando"
    st.session_state.listening_mensaje = ""

palabras_audio = ["cat", "dog", "house", "car", "tree", "sun"]
if "palabra_audio" not in st.session_state:
    st.session_state.palabra_audio = random.choice(palabras_audio)
if "listening_round" not in st.session_state:
    st.session_state.listening_round = 0
if "listening_estado" not in st.session_state:
    st.session_state.listening_estado = "esperando"
    st.session_state.listening_mensaje = ""

if boton_avanzar_presionado():
    nueva_palabra_listening()
    st.toast("🔘 ¡Botón físico! Siguiente palabra.", icon="⏭️")
    st.rerun()

palabra = st.session_state.palabra_audio

st.markdown("<div class='audio-icon'>🔊</div>", unsafe_allow_html=True)
st.markdown("### Escucha la palabra y escríbela:")

audio_data = obtener_audio(palabra)
if audio_data:
    st.audio(audio_data, format="audio/mp3")
else:
    st.warning("No se pudo generar el audio. Revisa tu internet. La palabra es para debug: " + palabra)

st.info("💡 Puedes presionar el botón físico de Wokwi en cualquier momento para saltar.")
mostrar_puntaje()

respuesta = st.text_input("Escribe la palabra que escuchaste:", key=f"input_listening_{st.session_state.listening_round}")

c1, c2 = st.columns(2)
with c1:
    btn_check = st.button("Comprobar ✅", use_container_width=True)
with c2:
    btn_skip = st.button("Saltar ⏭️", use_container_width=True)

if btn_skip:
    nueva_palabra_listening()
    st.rerun()

if btn_check:
    if not respuesta:
        st.warning("Por favor, escribe una palabra.")
    else:
        acierto = respuesta.lower().strip() == palabra.lower()
        mensaje = actualizar_puntaje(acierto)
        publicar_feedback(acierto)
        reproducir_feedback(acierto)
        st.session_state.listening_estado = "correcto" if acierto else "incorrecto"
        st.session_state.listening_mensaje = mensaje

# Mostrar estado persistente (no se borra con autorefresh)
if st.session_state.listening_estado == "correcto":
    st.success(st.session_state.listening_mensaje + " LED verde en Wokwi 🟢")
    if st.button("Siguiente palabra ➡️"):
        nueva_palabra_listening()
        st.rerun()
elif st.session_state.listening_estado == "incorrecto":
    st.error(st.session_state.listening_mensaje + f" Era: **{palabra}** LED rojo en Wokwi 🔴")
