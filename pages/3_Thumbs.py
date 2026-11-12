import streamlit as st
import tensorflow as tf
import numpy as np
import os
from PIL import Image, ImageOps
from streamlit_autorefresh import st_autorefresh
from utils import (inicializar_sesion, actualizar_puntaje, mostrar_puntaje,
                   publicar_feedback, reiniciar_ronda, reintentar,
                   hubo_avance_boton)

P = "thumbs"
PREGUNTAS = [
    {"espanol": "vaca",  "ingles": "cow",   "correcta": True},
    {"espanol": "perro", "ingles": "cat",   "correcta": False},
    {"espanol": "sol",   "ingles": "sun",   "correcta": True},
    {"espanol": "libro", "ingles": "table", "correcta": False},
]

st.set_page_config(page_title="Thumbs Up/Down", page_icon="👍", layout="centered")
st_autorefresh(interval=1000, key="refresh_thumbs")
inicializar_sesion()

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
    h1, h2, h3, p { color: #4a1c40 !important; }
    @keyframes shake { 0% { transform: rotate(0deg); } 25% { transform: rotate(-10deg); } 50% { transform: rotate(10deg); } 75% { transform: rotate(-10deg); } 100% { transform: rotate(0deg); } }
    .emoji-header { text-align: center; font-size: 80px; animation: shake 1s ease-in-out infinite; }
</style>
""", unsafe_allow_html=True)

st.title("👍 Pulgar Arriba / Abajo")

@st.cache_resource(show_spinner="Cargando modelo IA...")
def cargar_modelo():
    # Rutas corregidas (sin 'assets/')
    model_path = "thumbs_up.h5"
    labels_path = "labels.txt"
    
    if not os.path.exists(model_path):
        return None, f"❌ No se encuentra el archivo: {model_path}"
    if not os.path.exists(labels_path):
        return None, f"❌ No se encuentra el archivo: {labels_path}"

    try:
        model = tf.keras.models.load_model(model_path, compile=False)
        with open(labels_path, "r") as f:
            labels = [line.strip() for line in f.readlines() if line.strip()]
        return model, labels
    except Exception as e:
        return None, f"❌ Error al cargar Keras: {str(e)}"

def preprocesar_imagen(img: Image.Image) -> np.ndarray:
    size = (224, 224)
    image = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized = (image_array.astype(np.float32) / 127.0) - 1
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized
    return data

# Botón físico -> siguiente pregunta
if hubo_avance_boton(P):
    reiniciar_ronda(P, PREGUNTAS)
    st.toast("🔘 Botón de Wokwi: siguiente pregunta")
    st.rerun()

if f"{P}_actual" not in st.session_state:
    reiniciar_ronda(P, PREGUNTAS)

model, error_o_labels = cargar_modelo()

if model is None:
    st.error(error_o_labels)
    st.stop()

labels = error_o_labels

preg = st.session_state[f"{P}_actual"]
ronda = st.session_state[f"{P}_ronda"]
intento = st.session_state[f"{P}_intento"]
respondido = st.session_state[f"{P}_respondido"]

st.markdown("<div class='emoji-header'>👍 / 👎</div>", unsafe_allow_html=True)
st.markdown(f"### ¿La traducción de **{preg['espanol']}** es **{preg['ingles']}**?")
st.markdown("Muestra **pulgar arriba 👍** si es correcto, o **pulgar abajo 👎** si es incorrecto.")
st.info("💡 Puedes presionar el botón físico de Wokwi en cualquier momento para saltar.")
mostrar_puntaje()

img_file = st.camera_input(
    "Muestra tu pulgar a la cámara",
    key=f"{P}_cam_{ronda}_{intento}",
)

if img_file is not None:
    image = Image.open(img_file).convert("RGB")
    st.image(image, caption="Tu captura", use_container_width=True)

    if not respondido:
        data = preprocesar_imagen(image)
        prediction = model.predict(data, verbose=0)
        clase_idx = int(np.argmax(prediction))
        clase = labels[clase_idx]
        confianza = float(prediction[0][clase_idx])

        c = clase.lower()
        
        # Lógica adaptada a tus etiquetas: "0 Correcto", "1 Incorrecto", "2 Nada"
        if "incorrecto" in c or "down" in c or c.startswith("1"):
            gesto = False
        elif "correcto" in c or "up" in c or c.startswith("0"):
            gesto = True
        else: 
            gesto = None # Para "2 Nada"

        if gesto is None:
            resultado = {
                "acierto": None,
                "mensaje": f"Se detectó '{clase}' ({confianza:.2f}). No se reconoció un pulgar claro. Intenta de nuevo.",
                "clase": clase, 
                "conf": confianza
            }
        else:
            acierto = (gesto == preg["correcta"])
            mensaje = actualizar_puntaje(acierto)
            publicar_feedback(acierto)
            resultado = {
                "acierto": acierto, 
                "mensaje": mensaje,
                "clase": clase, 
                "conf": confianza
            }

        st.session_state[f"{P}_resultado"] = resultado
        st.session_state[f"{P}_respondido"] = True

resultado = st.session_state[f"{P}_resultado"]
if respondido and resultado:
    st.write(f"Predicción: **{resultado['clase']}** (confianza: {resultado['conf']:.2f})")
    
    if resultado["acierto"] is None:
        st.warning(resultado["mensaje"])
    elif resultado["acierto"]:
        st.success(resultado["mensaje"] + " LED verde en Wokwi 🟢")
    else:
        st.error(resultado["mensaje"] + " LED rojo en Wokwi 🔴")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔁 Intentar de nuevo"):
            reintentar(P)
            st.rerun()
    with c2:
        if st.button("➡️ Siguiente pregunta"):
            reiniciar_ronda(P, PREGUNTAS)
            st.rerun()
