import streamlit as st
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from utils import (inicializar_sesion, actualizar_puntaje, mostrar_puntaje,
                   publicar_feedback, reiniciar_ronda, reintentar,
                   hubo_avance_boton, normalizar)

P = "speaking"
PALABRAS = [
    "apple", "banana", "elephant", "computer", "beautiful", "language", 
    "dog", "cat", "house", "car", "tree", "sun", "moon", "star", 
    "book", "table", "chair", "water", "fire", "earth", "wind", 
    "heart", "brain", "music", "art", "science", "history", "math", 
    "teacher", "student", "school", "hospital", "doctor", "nurse", 
    "police", "engineer", "pilot", "chef", "waiter", "actor", 
    "singer", "dancer", "painter", "writer", "poet", "flower", 
    "mountain", "river", "ocean", "sky"
]

st.set_page_config(page_title="Speaking Practice", page_icon="🎤", layout="centered")
st_autorefresh(interval=1000, key="refresh_speaking")
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

# Botón físico -> siguiente palabra
if hubo_avance_boton(P):
    reiniciar_ronda(P, PALABRAS)
    st.toast("🔘 Botón de Wokwi: siguiente palabra")

if f"{P}_actual" not in st.session_state:
    reiniciar_ronda(P, PALABRAS)

palabra = st.session_state[f"{P}_actual"]
ronda = st.session_state[f"{P}_ronda"]
intento = st.session_state[f"{P}_intento"]

st.markdown("### Pronuncia la siguiente palabra:")
st.markdown(f"<div class='word-display'>{palabra}</div>", unsafe_allow_html=True)
mostrar_puntaje()

texto = speech_to_text(
    language="en",
    start_prompt="🎙️ Grabar",
    stop_prompt="⏹️ Detener",
    just_once=True,
    use_container_width=True,
    key=f"{P}_speech_{ronda}_{intento}",
)

# Evaluar UNA sola vez por intento
if texto and not st.session_state[f"{P}_respondido"]:
    acierto = normalizar(texto) == normalizar(palabra)
    mensaje = actualizar_puntaje(acierto)
    publicar_feedback(acierto)
    st.session_state[f"{P}_respondido"] = True
    st.session_state[f"{P}_resultado"] = {"acierto": acierto, "mensaje": mensaje, "dijo": texto}

resultado = st.session_state[f"{P}_resultado"]
if resultado:
    st.write(f"Has dicho: **{resultado['dijo']}**")
    if resultado["acierto"]:
        st.success(resultado["mensaje"])
    else:
        st.error(resultado["mensaje"])
        st.write(f"La palabra correcta es: **{palabra}**")
        if st.button("🔁 Intentar de nuevo"):
            reintentar(P)
            st.rerun()

    if st.button("➡️ Siguiente palabra"):
        reiniciar_ronda(P, PALABRAS)
        st.rerun()
