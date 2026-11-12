import streamlit as st
from streamlit_lottie import st_lottie
from utils import inicializar_sesion, mostrar_puntaje, cargar_lottie

st.set_page_config(
    page_title="English Play & Learn",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

inicializar_sesion()

# --- Estilo personalizado ---
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 20px;
        padding: 10px 24px;
        font-size: 18px;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
    }
    h1, h2, h3 {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Animación Lottie (reemplaza con tu propio archivo o URL) ---
lottie_hello = cargar_lottie("assets/lottie_home.json") # O usa: load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_u4yrau.json")
col1, col2 = st.columns([1, 1])
with col1:
    st.title("🎓 English Play & Learn")
    st.markdown("""
    ### Aprende inglés de forma lúdica y multimodal
    Esta aplicación te permite practicar **speaking**, **listening** y **vocabulario** 
    utilizando tu voz, la cámara y el teclado. ¡Cada acierto suma puntos!
    """)
    mostrar_puntaje()
    st.info("👈 Selecciona una actividad en la barra lateral para comenzar.")
with col2:
    st_lottie(lottie_hello, height=400, key="hello")

st.divider()
st.subheader("🎯 Actividades disponibles")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### 🎤 Speaking")
    st.write("Pronuncia la palabra que ves en pantalla.")
    st.page_link("pages/1_Speaking.py", label="Ir a Speaking →", icon="🎤")
with c2:
    st.markdown("### 🎧 Listening")
    st.write("Escucha una palabra y escríbela correctamente.")
    st.page_link("pages/2_Listening.py", label="Ir a Listening →", icon="🎧")
with c3:
    st.markdown("### 👍 Thumbs Up/Down")
    st.write("Muestra pulgar arriba o abajo según la traducción.")
    st.page_link("pages/3_Thumbs.py", label="Ir a Thumbs →", icon="👍")
