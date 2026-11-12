import streamlit as st
from utils import (inicializar_sesion, mostrar_puntaje,
                   inject_global_css, animated_bg, floating_emojis)

st.set_page_config(
    page_title="English Play & Learn 🎮",
    page_icon="🌈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_css()
animated_bg("#a8e6ff", "#ffb3f0", "#c9a3ff", speed=18)
floating_emojis(["🌈", "⭐", "🎮", "🎨", "🧩", "🎯", "🌟", "🎪"])
inicializar_sesion()

st.markdown("""
<style>
    .hero-title {
        font-family: 'Baloo 2', sans-serif;
        font-weight: 800;
        font-size: clamp(2.5rem, 6vw, 4.5rem);
        text-align: center;
        background: linear-gradient(90deg,#ff6b9d,#ffb84d,#6bffb8,#5bb8ff,#c77dff,#ff6b9d);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: rainbowText 4s linear infinite;
        line-height: 1.1;
        margin: 1rem 0 0.3rem;
        filter: drop-shadow(3px 5px 10px rgba(0,0,0,0.18));
    }
    @keyframes rainbowText {
        0%   { background-position: 0% 50%; }
        100% { background-position: 300% 50%; }
    }
    .hero-sub {
        text-align: center;
        font-size: 1.35rem;
        font-weight: 600;
        color: #4a1c40;
        margin-bottom: 1.5rem;
    }
    .hero-badge {
        text-align: center;
        font-size: 6rem;
        animation: badgeFloat 3s ease-in-out infinite;
        filter: drop-shadow(0 15px 25px rgba(0,0,0,0.25));
        margin: 0.5rem 0;
    }
    @keyframes badgeFloat {
        0%, 100% { transform: translateY(0) rotate(-5deg); }
        50%      { transform: translateY(-20px) rotate(5deg); }
    }
    .card-act {
        background: rgba(255,255,255,0.88);
        backdrop-filter: blur(12px);
        border-radius: 32px;
        padding: 2rem 1.5rem 1.4rem;
        text-align: center;
        box-shadow: 0 12px 34px rgba(0,0,0,0.15);
        border: 4px solid #fff;
        transition: all 0.3s cubic-bezier(.34,1.56,.64,1);
        margin-bottom: 1rem;
    }
    .card-act:hover {
        transform: translateY(-12px) scale(1.03);
        box-shadow: 0 22px 44px rgba(0,0,0,0.22);
    }
    .card-act .c-emoji {
        font-size: 4.5rem;
        display: block;
        margin-bottom: 0.4rem;
        animation: bounceEmoji 2s ease-in-out infinite;
    }
    @keyframes bounceEmoji {
        0%, 100% { transform: translateY(0) scale(1); }
        50%      { transform: translateY(-12px) scale(1.08); }
    }
    .card-act h3 {
        font-family: 'Baloo 2', sans-serif;
        font-weight: 800;
        font-size: 1.7rem;
        color: #4a1c40;
        margin: 0.3rem 0;
    }
    .card-act p {
        font-family: 'Fredoka', sans-serif;
        font-size: 1rem;
        color: #6a4c6a;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------- HERO ----------
st.markdown('<div class="hero-badge">🌍✨🎓</div>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">English Play & Learn</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">🌈 ¡Aprende inglés jugando con Wokwi! 🎮</p>', unsafe_allow_html=True)

mostrar_puntaje()

# ---------- TARJETAS ----------
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
    <div class="card-act">
        <span class="c-emoji">🎤</span>
        <h3>Habla</h3>
        <p>Di la palabra en voz alta y gana puntos</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🎤 ¡Jugar Speaking!", key="go_speak", use_container_width=True):
        st.switch_page("pages/1_Speaking.py")

with col2:
    st.markdown("""
    <div class="card-act">
        <span class="c-emoji">🎧</span>
        <h3>Escucha</h3>
        <p>Escucha y escribe la palabra secreta</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🎧 ¡Jugar Listening!", key="go_listen", use_container_width=True):
        st.switch_page("pages/2_Listening.py")

with col3:
    st.markdown("""
    <div class="card-act">
        <span class="c-emoji">👍</span>
        <h3>Pulgares</h3>
        <p>¡Muestra tu pulgar a la cámara!</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("👍 ¡Jugar Thumbs!", key="go_thumbs", use_container_width=True):
        st.switch_page("pages/3_Thumbs.py")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;">
    <div class="wokwi-banner" style="display:inline-flex;">
        <span class="w-icon">🔘</span>
        <span>Presiona el botón físico de Wokwi para avanzar en cualquier juego</span>
    </div>
</div>
""", unsafe_allow_html=True)
