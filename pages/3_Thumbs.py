import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import random
from streamlit_autorefresh import st_autorefresh
from utils import (inicializar_sesion, actualizar_puntaje, mostrar_puntaje, 
                   publicar_feedback, obtener_ultimo_mensaje_boton)

st.set_page_config(page_title="Thumbs Up/Down", page_icon="👍", layout="centered")

# ESTA LÍNEA ES CLAVE PARA QUE EL BOTÓN DE WOKWI FUNCIONE
st_autorefresh(interval=1500, key="mqtt_refresh_thumbs")

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

@st.cache_resource
def cargar_modelo():
    try:
        model = tf.keras.models.load_model("assets/thumbs_up.h5")
        with open("assets/labels.txt", "r") as f:
            labels = [line.strip() for line in f.readlines()]
        return model, labels
    except Exception as e:
        return None, None

model, labels = cargar_modelo()

if model is None:
    st.error("⚠️ Error al cargar el modelo. Asegúrate de tener 'thumbs_up.h5' y 'labels.txt' en la carpeta assets/.")
    st.stop()

mensaje_boton = obtener_ultimo_mensaje_boton()
if mensaje_boton == "AVANZAR":
    if "pregunta_actual" in st.session_state:
        del st.session_state.pregunta_actual
    st.toast("🔘 ¡Botón de Wokwi presionado! Siguiente pregunta.")

preguntas = [
    {"espanol": "vaca", "ingles": "cow", "correcta": True},
    {"espanol": "perro", "ingles": "cat", "correcta": False},
    {"espanol": "sol", "ingles": "sun", "correcta": True},
    {"espanol": "libro", "ingles": "table", "correcta": False},
]

if "pregunta_actual" not in st.session_state:
    st.session_state.pregunta_actual = random.choice(preguntas)

preg = st.session_state.pregunta_actual

st.markdown("<div class='emoji-header'>👍 / 👎</div>", unsafe_allow_html=True)
st.markdown(f"### ¿La traducción de **{preg['espanol']}** es **{preg['ingles']}**?")
st.markdown("Muestra **pulgar arriba 👍** si es correcto, o **pulgar abajo 👎** si es incorrecto.")

mostrar_puntaje()

img_file = st.camera_input("Muestra tu pulgar a la cámara")

def preprocesar_imagen(img: Image.Image) -> np.ndarray:
    size = (224, 224)
    image = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized = (image_array.astype(np.float32) / 127.0) - 1
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized
    return data

if img_file is not None:
    image = Image.open(img_file).convert("RGB")
    st.image(image, caption="Tu captura", use_column_width=True)
    data = preprocesar_imagen(image)
    prediction = model.predict(data)
    clase_idx = np.argmax(prediction)
    clase = labels[clase_idx]
    confianza = prediction[0][clase_idx]

    st.write(f"Predicción: **{clase}** (confianza: {confianza:.2f})")

    if "up" in clase.lower() or "arriba" in clase.lower():
        usuario_dice_correcto = True
    elif "down" in clase.lower() or "abajo" in clase.lower():
        usuario_dice_correcto = False
    else:
        st.warning("No se reconoció el gesto. Intenta de nuevo.")
        st.stop()

    acierto = (usuario_dice_correcto == preg["correcta"])
    mensaje = actualizar_puntaje(acierto)
    publicar_feedback(acierto)

    if acierto:
        st.success(mensaje)
    else:
        st.error(mensaje)

    if st.button("Siguiente pregunta ➡️"):
        st.session_state.pregunta_actual = random.choice(preguntas)
        st.rerun()
