import streamlit as st
from streamlit_autorefresh import st_autorefresh
from utils import inicializar_sesion, mostrar_puntaje

st.set_page_config(page_title="English Play & Learn", page_icon="🎮", layout="wide")

st_autorefresh(interval=1000, key="mqtt_refresh")

inicializar_sesion()

st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    h1, h2, h3 { color: #ffffff !important; }
    .stButton>button { background-color: #4CAF50; color: white; border-radius: 20px; padding: 10px 24px; font-size: 18px; transition: transform 0.2s; }
    .stButton>button:hover { transform: scale(1.05); }
    @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }
    .floating-emoji { font-size: 120px; text-align: center; animation: float 3s ease-in-out infinite; }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 1])

with col1:
    st.title("🎓 English Play & Learn")
    st.markdown("""
    ### Aprende inglés de forma lúdica y multimodal
    Esta aplicación está conectada a tu placa física (simulada en Wokwi).
    Presiona el **botón rojo** en Wokwi para avanzar de pregunta.
    """)
    mostrar_puntaje()
    st.info("Selecciona una actividad en la barra lateral para comenzar.")

with col2:
    st.markdown("<div class='floating-emoji'>🌍🗣️</div>", unsafe_allow_html=True)

st.divider()

st.subheader("🎯 Actividades disponibles")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("### 🎤 Speaking")
    st.write("Pronuncia la palabra que ves en pantalla.")
    st.page_link("pages/1_Speaking.py", label="Ir a Speaking", icon="🎤")

with c2:
    st.markdown("### 🎧 Listening")
    st.write("Escucha una palabra y escríbela correctamente.")
    st.page_link("pages/2_Listening.py", label="Ir a Listening", icon="🎧")

with c3:
    st.markdown("### 👍 Thumbs Up/Down")
    st.write("Muestra pulgar arriba o abajo según la traducción.")
    st.page_link("pages/3_Thumbs.py", label="Ir a Thumbs", icon="👍")
