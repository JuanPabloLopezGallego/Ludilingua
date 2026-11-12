import streamlit as st
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from utils import (inicializar_sesion, actualizar_puntaje, mostrar_puntaje,
                   publicar_feedback, reproducir_feedback, boton_avanzar_presionado)
import random

st.set_page_config(page_title="Speaking Practice", page_icon="🎤", layout="centered")
# 4 segundos para permitir grabar sin cortes
st_autorefresh(interval=4000, key="mqtt_refresh_speaking")
inicializar_sesion()

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    h1, h2, h3, p { color: #ffffff !important; }
    .word-display { text-align: center; font-size: 90px; font-weight: bold; color: #fff; text-shadow: 2px 2px 8px rgba(0,0,0,0.3); }
</style>
""", unsafe_allow_html=True)

st.title("🎤 Práctica de Pronunciación")

palabras = ["apple", "banana", "elephant", "computer", "beautiful", "language"]

if "palabra_actual" not in st.session_state:
    st.session_state.palabra_actual = random.choice(palabras)
if "speaking_round" not in st.session_state:
    st.session_state.speaking_round = 0
if "speaking_procesado" not in st.session_state:
    st.session_state.speaking_procesado = None

# BOTÓN FÍSICO -> cambiar palabra en cualquier momento
if boton_avanzar_presionado():
    actual = st.session_state.palabra_actual
    opciones = [p for p in palabras if p != actual]
    st.session_state.palabra_actual = random.choice(opciones)
    st.session_state.speaking_round += 1
    st.session_state.speaking_procesado = None
    st.toast("🔘 ¡Botón físico! Siguiente palabra.", icon="⏭️")
    st.rerun()

palabra = st.session_state.palabra_actual
st.markdown("### Pronuncia la siguiente palabra:")
st.markdown(f"<div class='word-display'>{palabra}</div>", unsafe_allow_html=True)
st.info("💡 Puedes presionar el botón físico de Wokwi en cualquier momento para saltar.")

mostrar_puntaje()

texto_reconocido = speech_to_text(
    language='en',
    start_prompt="🎙️ Grabar",
    stop_prompt="⏹️ Detener",
    just_once=True,
    use_container_width=True,
    key=f"speech_{st.session_state.speaking_round}"
)

if texto_reconocido:
    texto_limpio = texto_reconocido.lower().strip()
    st.write(f"Has dicho: **{texto_reconocido}**")
    clave = f"{texto_limpio}|{palabra}|{st.session_state.speaking_round}"

    # Solo puntuar/publicar UNA vez por respuesta (evita puntos infinitos)
    if st.session_state.speaking_procesado != clave:
        acierto = (texto_limpio == palabra.lower())
        mensaje = actualizar_puntaje(acierto)
        publicar_feedback(acierto)  # -> LED + Buzzer físico
        reproducir_feedback(acierto)  # sonido local
        st.session_state.speaking_procesado = clave
        st.session_state.speaking_acierto = acierto
        st.session_state.speaking_mensaje = mensaje
    else:
        acierto = st.session_state.get("speaking_acierto", False)
        mensaje = st.session_state.get("speaking_mensaje", "")

    if acierto:
        st.success(mensaje + " LED verde en Wokwi 🟢")
    else:
        st.error(mensaje + f" La palabra era: **{palabra}** LED rojo en Wokwi 🔴")

colA, colB = st.columns(2)
with colA:
    if st.button("Siguiente palabra ⏭️", use_container_width=True):
        actual = st.session_state.palabra_actual
        opciones = [p for p in palabras if p != actual]
        st.session_state.palabra_actual = random.choice(opciones)
        st.session_state.speaking_round += 1
        st.session_state.speaking_procesado = None
        st.rerun()
