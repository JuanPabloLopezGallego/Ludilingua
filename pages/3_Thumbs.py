import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import random
from utils import inicializar_sesion, actualizar_puntaje, mostrar_puntaje, reproducir_feedback

st.set_page_config(page_title="Thumbs Up/Down", page_icon="👍", layout="centered")
inicializar_sesion()

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    h1, h2, p {
        color: #4a1c40 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("👍 Pulgar Arriba / Abajo")

# --- Cargar modelo de Teachable Machine ---
@st.cache_resource
def cargar_modelo():
    model = tf.keras.models.load_model("assets/thumbs_up.h5")
    with open("assets/labels.txt", "r") as f:
        labels = [line.strip() for line in f.readlines()]
    return model, labels

try:
    model, labels = cargar_modelo()
except Exception as e:
    st.error(f"Error al cargar el modelo: {e}. Asegúrate de tener 'thumbs_up.h5' y 'labels.txt' en la carpeta assets/.")
    st.stop()

# --- Preguntas de ejemplo ---
preguntas = [
    {"espanol": "vaca", "ingles": "cow", "correcta": True},
    {"espanol": "perro", "ingles": "cat", "correcta": False},
    {"espanol": "sol", "ingles": "sun", "correcta": True},
    {"espanol": "libro", "ingles": "table", "correcta": False},
]

if "pregunta_actual" not in st.session_state:
    st.session_state.pregunta_actual = random.choice(preguntas)

preg = st.session_state.pregunta_actual
st.markdown(f"### ¿La traducción de **{preg['espanol']}** es **{preg['ingles']}**?")
st.markdown("Muestra **pulgar arriba 👍** si es correcto, o **pulgar abajo 👎** si es incorrecto.")

mostrar_puntaje()

# --- Captura de cámara ---
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

    # Mapeo: asumimos que labels.txt contiene "Thumbs Up" y "Thumbs Down"
    if "up" in clase.lower() or "arriba" in clase.lower():
        usuario_dice_correcto = True
    elif "down" in clase.lower() or "abajo" in clase.lower():
        usuario_dice_correcto = False
    else:
        st.warning("No se reconoció el gesto. Intenta de nuevo.")
        st.stop()

    acierto = (usuario_dice_correcto == preg["correcta"])
    mensaje = actualizar_puntaje(acierto)
    reproducir_feedback(acierto)

    if acierto:
        st.success(mensaje)
    else:
        st.error(mensaje)

    if st.button("Siguiente pregunta ➡️"):
        st.session_state.pregunta_actual = random.choice(preguntas)
        st.rerun()
