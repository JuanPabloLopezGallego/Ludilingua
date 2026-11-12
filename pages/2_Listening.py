import streamlit as st
from gtts import gTTS
from io import BytesIO
from streamlit_autorefresh import st_autorefresh
from utils import (inicializar_sesion, actualizar_puntaje, mostrar_puntaje,
                   publicar_feedback, reiniciar_ronda, reintentar,
                   hubo_avance_boton, normalizar)

P = "listening"
PALABRAS = [
    "cat", "dog", "house", "car", "tree", "sun", "moon", "star", 
    "book", "table", "chair", "water", "fire", "earth", "wind", 
    "apple", "banana", "orange", "grape", "strawberry", "elephant", 
    "lion", "tiger", "monkey", "giraffe", "zebra", "computer", 
    "phone", "television", "radio", "music", "guitar", "piano", 
    "drum", "violin", "flute", "school", "teacher", "student", 
    "doctor", "nurse", "police", "engineer", "pilot", "chef"
]

st.set_page_config(page_title="Listening Practice", page_icon="🎧", layout="centered")
st_autorefresh(interval=1000, key="refresh_listening")
inicializar_sesion()

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    h1, h2, h3, p { color: #0a2e5c !important; }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }
    .audio-icon { text-align: center; font-size: 80px; animation: pulse 2s infinite; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def audio_palabra(palabra: str) -> bytes:
    buffer = BytesIO()
    gTTS(text=palabra, lang="en").write_to_fp(buffer)
    return buffer.getvalue()


st.title("🎧 Escucha y Escribe")

if hubo_avance_boton(P):
    reiniciar_ronda(P, PALABRAS)
    st.toast("🔘 Botón de Wokwi: siguiente palabra")

if f"{P}_actual" not in st.session_state:
    reiniciar_ronda(P, PALABRAS)

palabra = st.session_state[f"{P}_actual"]
ronda = st.session_state[f"{P}_ronda"]
intento = st.session_state[f"{P}_intento"]
respondido = st.session_state[f"{P}_respondido"]

st.markdown("<div class='audio-icon'>🔊</div>", unsafe_allow_html=True)
st.markdown("### Escucha la palabra y escríbela:")
st.audio(audio_palabra(palabra), format="audio/mp3")
mostrar_puntaje()

respuesta = st.text_input(
    "Escribe la palabra que escuchaste:",
    key=f"{P}_input_{ronda}_{intento}",
    disabled=respondido,
)

if not respondido:
    if st.button("✅ Comprobar", key=f"{P}_btn_{ronda}_{intento}"):
        if respuesta.strip():
            acierto = normalizar(respuesta) == normalizar(palabra)
            mensaje = actualizar_puntaje(acierto)
            publicar_feedback(acierto)
            st.session_state[f"{P}_respondido"] = True
            st.session_state[f"{P}_resultado"] = {
                "acierto": acierto, "mensaje": mensaje, "dijo": respuesta.strip()
            }
            st.rerun()
        else:
            st.warning("Por favor, escribe una palabra.")

resultado = st.session_state[f"{P}_resultado"]
if respondido and resultado:
    st.write(f"Escribiste: **{resultado['dijo']}**")
    if resultado["acierto"]:
        st.success(resultado["mensaje"])
    else:
        st.error(resultado["mensaje"])
        st.write(f"La palabra correcta era: **{palabra}**")
        if st.button("🔁 Intentar de nuevo"):
            reintentar(P)
            st.rerun()

    if st.button("➡️ Siguiente palabra"):
        reiniciar_ronda(P, PALABRAS)
        st.rerun()
