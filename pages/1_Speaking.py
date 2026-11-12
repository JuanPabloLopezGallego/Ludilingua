import streamlit as st
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from utils import (inicializar_sesion, actualizar_puntaje, mostrar_puntaje,
                   publicar_feedback, reiniciar_ronda, hubo_avance_boton,
                   normalizar, inject_global_css, animated_bg, floating_emojis,
                   kid_alert, wokwi_hint)

P = "speaking"
PALABRAS = [
    "apple","banana","elephant","computer","beautiful","language","dog","cat",
    "house","car","tree","sun","moon","star","book","table","chair","water",
    "fire","earth","wind","heart","brain","music","art","science","history",
    "math","teacher","student","school","hospital","doctor","nurse","police",
    "engineer","pilot","chef","waiter","actor","singer","dancer","painter",
    "writer","poet","flower","mountain","river","ocean","sky"
]

st.set_page_config(page_title="Speaking Practice", page_icon="🎤", layout="centered")
inject_global_css()
animated_bg("#ff6b9d", "#c77dff", "#ff9e7d", speed=14)
floating_emojis(["✨","🌟","⭐","🎤","🎵","💖"])
st_autorefresh(interval=1000, key="refresh_speaking")
inicializar_sesion()

st.markdown("""
<style>
    .speak-title {
        text-align: center;
        font-family: 'Baloo 2', sans-serif;
        font-weight: 800;
        font-size: clamp(1.8rem, 4.5vw, 3.2rem);
        color: #fff;
        text-shadow: 3px 3px 0 #ff4d94, 6px 6px 22px rgba(0,0,0,0.35);
        margin: 0.3rem 0 0.2rem;
        animation: titleWiggle 3s ease-in-out infinite;
    }
    @keyframes titleWiggle {
        0%, 100% { transform: rotate(-1deg); }
        50%      { transform: rotate(1deg); }
    }
    .mic-display {
        text-align: center;
        font-size: 5.5rem;
        animation: micPulse 1.6s ease-in-out infinite;
        filter: drop-shadow(0 0 22px rgba(255,107,157,0.9));
        margin: 0.4rem 0;
    }
    @keyframes micPulse {
        0%, 100% { transform: scale(1) rotate(-6deg); }
        50%      { transform: scale(1.18) rotate(6deg); }
    }
    .word-bubble {
        display: block;
        text-align: center;
        font-family: 'Baloo 2', sans-serif;
        font-weight: 800;
        font-size: clamp(2.4rem, 8vw, 5rem);
        background: linear-gradient(135deg, #ffffff 0%, #ffe6f3 100%);
        padding: 1.8rem 2rem;
        border-radius: 50px;
        margin: 1rem auto;
        max-width: 92%;
        box-shadow: 0 18px 40px rgba(0,0,0,0.25), inset 0 -8px 0 rgba(0,0,0,0.08);
        border: 6px solid #fff;
        color: #c2185b;
        letter-spacing: 3px;
        position: relative;
        animation: bubblePop 0.6s cubic-bezier(.34,1.56,.64,1);
    }
    @keyframes bubblePop {
        0%   { transform: scale(0.3) rotate(-8deg); opacity: 0; }
        100% { transform: scale(1) rotate(0deg); opacity: 1; }
    }
    .word-bubble::before, .word-bubble::after {
        content: '✨';
        position: absolute;
        font-size: 2rem;
        animation: sparkle 2s linear infinite;
    }
    .word-bubble::before { top: -8px; left: 18px; }
    .word-bubble::after  { bottom: -8px; right: 18px; animation-direction: reverse; }
    @keyframes sparkle {
        0%, 100% { transform: rotate(0deg) scale(1); opacity: 1; }
        50%      { transform: rotate(180deg) scale(1.4); opacity: 0.7; }
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="speak-title">🎤 ¡A Pronunciar!</h1>', unsafe_allow_html=True)
st.markdown('<div class="mic-display">🎙️</div>', unsafe_allow_html=True)

# ---------- BOTÓN WOKWI ----------
if hubo_avance_boton(P):
    reiniciar_ronda(P, PALABRAS)
    st.toast("🔘 ¡Siguiente palabra!", icon="🎮")
    st.rerun()

if f"{P}_actual" not in st.session_state:
    reiniciar_ronda(P, PALABRAS)

palabra = st.session_state[f"{P}_actual"]
ronda = st.session_state[f"{P}_ronda"]
intento = st.session_state[f"{P}_intento"]

st.markdown(
    f"<div class='word-bubble'>{palabra}</div>",
    unsafe_allow_html=True,
)
mostrar_puntaje()

texto = speech_to_text(
    language="en",
    start_prompt="🎙️ Grabar",
    stop_prompt="⏹️ Detener",
    just_once=True,
    use_container_width=True,
    key=f"{P}_speech_{ronda}_{intento}",
)

# ---------- EVALUACIÓN ----------
if texto and not st.session_state[f"{P}_respondido"]:
    acierto = normalizar(texto) == normalizar(palabra)
    mensaje = actualizar_puntaje(acierto)
    publicar_feedback(acierto)
    st.session_state[f"{P}_respondido"] = True
    st.session_state[f"{P}_resultado"] = {
        "acierto": acierto, "mensaje": mensaje, "dijo": texto
    }
    if acierto:
        st.balloons()

resultado = st.session_state[f"{P}_resultado"]
if resultado:
    st.markdown(
        f"<p style='text-align:center;color:#fff;font-size:1.2rem;font-weight:600;"
        f"text-shadow:1px 1px 6px rgba(0,0,0,0.4);'>Tú dijiste: <strong>{resultado['dijo']}</strong></p>",
        unsafe_allow_html=True,
    )
    if resultado["acierto"]:
        kid_alert("success", f"¡Excelente! {resultado['mensaje']}")
    else:
        kid_alert("error", f"¡Casi! La palabra era <strong>{palabra}</strong>. {resultado['mensaje']}")
    wokwi_hint("Presiona el botón de Wokwi para la siguiente palabra")
