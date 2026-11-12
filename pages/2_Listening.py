import streamlit as st
from gtts import gTTS
from io import BytesIO
from streamlit_autorefresh import st_autorefresh
from utils import (inicializar_sesion, actualizar_puntaje, mostrar_puntaje,
                   publicar_feedback, reiniciar_ronda, hubo_avance_boton,
                   normalizar, inject_global_css, animated_bg, floating_emojis,
                   kid_alert, wokwi_hint)

P = "listening"
PALABRAS = [
    "cat","dog","house","car","tree","sun","moon","star","book","table",
    "chair","water","fire","earth","wind","apple","banana","orange","grape",
    "strawberry","elephant","lion","tiger","monkey","giraffe","zebra",
    "computer","phone","television","radio","music","guitar","piano","drum",
    "violin","flute","school","teacher","student","doctor","nurse","police",
    "engineer","pilot","chef"
]

st.set_page_config(page_title="Listening Practice", page_icon="🎧", layout="centered")
inject_global_css()
animated_bg("#4facfe", "#00f2fe", "#6be3ff", speed=14)
floating_emojis(["🌊","🐠","🐟","🎧","🎵","💙"])
st_autorefresh(interval=1000, key="refresh_listening")
inicializar_sesion()

st.markdown("""
<style>
    .listen-title {
        text-align: center;
        font-family: 'Baloo 2', sans-serif;
        font-weight: 800;
        font-size: clamp(1.8rem, 4.5vw, 3.2rem);
        color: #fff;
        text-shadow: 3px 3px 0 #0077cc, 6px 6px 22px rgba(0,0,0,0.35);
        margin: 0.3rem 0 0.2rem;
        animation: titleBob 2.5s ease-in-out infinite;
    }
    @keyframes titleBob {
        0%, 100% { transform: translateY(0); }
        50%      { transform: translateY(-6px); }
    }
    .headphone-display {
        text-align: center;
        font-size: 5.5rem;
        animation: headBob 1.8s ease-in-out infinite;
        filter: drop-shadow(0 0 22px rgba(79,172,254,0.9));
        margin: 0.4rem 0;
    }
    @keyframes headBob {
        0%, 100% { transform: rotate(-8deg); }
        50%      { transform: rotate(8deg); }
    }
    /* Visualizador de ondas */
    .waves-box {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 6px;
        height: 70px;
        margin: 1rem 0;
    }
    .wave-bar {
        width: 10px;
        background: linear-gradient(180deg, #00f2fe, #4facfe);
        border-radius: 6px;
        animation: waveUpDown 1s ease-in-out infinite;
        box-shadow: 0 4px 12px rgba(79,172,254,0.5);
    }
    .wave-bar:nth-child(1) { animation-delay: 0.0s; height: 30%; }
    .wave-bar:nth-child(2) { animation-delay: 0.1s; height: 60%; }
    .wave-bar:nth-child(3) { animation-delay: 0.2s; height: 95%; }
    .wave-bar:nth-child(4) { animation-delay: 0.3s; height: 70%; }
    .wave-bar:nth-child(5) { animation-delay: 0.4s; height: 45%; }
    .wave-bar:nth-child(6) { animation-delay: 0.5s; height: 80%; }
    .wave-bar:nth-child(7) { animation-delay: 0.6s; height: 55%; }
    .wave-bar:nth-child(8) { animation-delay: 0.7s; height: 35%; }
    @keyframes waveUpDown {
        0%, 100% { transform: scaleY(0.5); }
        50%      { transform: scaleY(1); }
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="listen-title">🎧 ¡Escucha y Escribe!</h1>', unsafe_allow_html=True)
st.markdown('<div class="headphone-display">🎧</div>', unsafe_allow_html=True)

@st.cache_data
def audio_palabra(palabra: str) -> bytes:
    buf = BytesIO()
    gTTS(text=palabra, lang="en").write_to_fp(buf)
    return buf.getvalue()

if hubo_avance_boton(P):
    reiniciar_ronda(P, PALABRAS)
    st.toast("🔘 ¡Siguiente palabra!", icon="🎮")
    st.rerun()

if f"{P}_actual" not in st.session_state:
    reiniciar_ronda(P, PALABRAS)

palabra = st.session_state[f"{P}_actual"]
ronda = st.session_state[f"{P}_ronda"]
intento = st.session_state[f"{P}_intento"]
respondido = st.session_state[f"{P}_respondido"]

# ---------- ONDAS ----------
st.markdown("""
<div class="waves-box">
    <div class="wave-bar"></div><div class="wave-bar"></div>
    <div class="wave-bar"></div><div class="wave-bar"></div>
    <div class="wave-bar"></div><div class="wave-bar"></div>
    <div class="wave-bar"></div><div class="wave-bar"></div>
</div>
""", unsafe_allow_html=True)

st.audio(audio_palabra(palabra), format="audio/mp3")
mostrar_puntaje()

respuesta = st.text_input(
    "✏️ Escribe la palabra que escuchaste:",
    key=f"{P}_input_{ronda}_{intento}",
    disabled=respondido,
    placeholder="Escribe aquí...",
)

if not respondido:
    if st.button("✅ ¡Comprobar!", key=f"{P}_btn_{ronda}_{intento}", use_container_width=True):
        if respuesta.strip():
            acierto = normalizar(respuesta) == normalizar(palabra)
            mensaje = actualizar_puntaje(acierto)
            publicar_feedback(acierto)
            st.session_state[f"{P}_respondido"] = True
            st.session_state[f"{P}_resultado"] = {
                "acierto": acierto, "mensaje": mensaje, "dijo": respuesta.strip()
            }
            if acierto:
                st.balloons()
            st.rerun()
        else:
            st.warning("¡Escribe una palabra primero! ✍️")

resultado = st.session_state[f"{P}_resultado"]
if respondido and resultado:
    if resultado["acierto"]:
        kid_alert("success", f"¡Excelente! {resultado['mensaje']}")
    else:
        kid_alert("error", f"¡Casi! La palabra era <strong>{palabra}</strong>. {resultado['mensaje']}")
    wokwi_hint("Presiona el botón de Wokwi para la siguiente palabra")
