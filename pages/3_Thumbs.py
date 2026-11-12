import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import random
import hashlib
from streamlit_autorefresh import st_autorefresh
from utils import (
    inicializar_sesion, actualizar_puntaje, mostrar_puntaje,
    publicar_feedback, obtener_ultimo_mensaje_boton, elegir_siguiente_item
)

st.set_page_config(page_title="Thumbs Up/Down", page_icon="👍", layout="centered")

st_autorefresh(interval=1500, key="mqtt_refresh_thumbs")

inicializar_sesion()

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
    h1, h2, h3, p { color: #4a1c40 !important; }
    @keyframes shake { 0% { transform: rotate(0deg); } 25% { transform: rotate(-8deg); } 50% { transform: rotate(8deg); } 75% { transform: rotate(-8deg); } 100% { transform: rotate(0deg); } }
    .emoji-header { text-align: center; font-size: 72px; animation: shake 1.2s ease-in-out infinite; }
</style>
""", unsafe_allow_html=True)

st.title("👍 Pulgar Arriba / Abajo")


@st.cache_resource
def cargar_modelo():
    try:
        model = tf.keras.models.load_model("assets/thumbs_up.h5", compile=False)
        with open("assets/labels.txt", "r", encoding="utf-8") as f:
            labels = [line.strip() for line in f.readlines()]
        return model, labels
    except Exception:
        return None, None


model, labels = cargar_modelo()

if model is None:
    st.error("⚠️ Error al cargar el modelo. Asegúrate de tener 'thumbs_up.h5' y 'labels.txt' en la carpeta assets/.")
    st.stop()

preguntas = [
    {"espanol": "vaca", "ingles": "cow", "correcta": True},
    {"espanol": "perro", "ingles": "cat", "correcta": False},
    {"espanol": "sol", "ingles": "sun", "correcta": True},
    {"espanol": "libro", "ingles": "table", "correcta": False},
    {"espanol": "agua", "ingles": "water", "correcta": True},
    {"espanol": "manzana", "ingles": "chair", "correcta": False},
]

if "pregunta_actual" not in st.session_state:
    st.session_state.pregunta_actual = random.choice(preguntas)
if "cam_step" not in st.session_state:
    st.session_state.cam_step = 0
if "ultima_foto_hash" not in st.session_state:
    st.session_state.ultima_foto_hash = None
if "thumbs_resultado" not in st.session_state:
    st.session_state.thumbs_resultado = None


def avanzar_pregunta():
    st.session_state.pregunta_actual = elegir_siguiente_item(preguntas, st.session_state.pregunta_actual)
    st.session_state.cam_step += 1  # Limpia la foto anterior de la cámara automáticamente
    st.session_state.ultima_foto_hash = None
    st.session_state.thumbs_resultado = None


# Detectar botón físico de Wokwi
if obtener_ultimo_mensaje_boton() == "AVANZAR":
    avanzar_pregunta()
    st.toast("🔘 ¡Botón de Wokwi presionado! Siguiente pregunta.", icon="👍")

preg = st.session_state.pregunta_actual
mostrar_puntaje()

st.markdown("<div class='emoji-header'>👍 / 👎</div>", unsafe_allow_html=True)
st.markdown(f"### ¿La traducción de **{preg['espanol']}** es **{preg['ingles']}**?")
st.markdown("Muestra **pulgar arriba 👍** si es correcto, o **pulgar abajo 👎** si es incorrecto.")

img_file = st.camera_input(
    "Muestra tu pulgar a la cámara",
    key=f"cam_{st.session_state.cam_step}"
)


def preprocesar_imagen(img: Image.Image) -> np.ndarray:
    size = (224, 224)
    image = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized = (image_array.astype(np.float32) / 127.5) - 1.0
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized
    return data


if img_file is not None:
    raw_bytes = img_file.getvalue()
    foto_hash = hashlib.md5(raw_bytes).hexdigest()

    # Solo procesamos y enviamos MQTT UNA VEZ por cada foto nueva tomada
    if foto_hash != st.session_state.ultima_foto_hash:
        st.session_state.ultima_foto_hash = foto_hash
        image = Image.open(img_file).convert("RGB")
        data = preprocesar_imagen(image)
        prediction = model.predict(data, verbose=0)
        clase_idx = int(np.argmax(prediction))
        clase = labels[clase_idx]
        confianza = float(prediction[0][clase_idx])

        if "up" in clase.lower() or "arriba" in clase.lower():
            usuario_dice_correcto = True
        elif "down" in clase.lower() or "abajo" in clase.lower():
            usuario_dice_correcto = False
        else:
            usuario_dice_correcto = None

        if usuario_dice_correcto is None:
            st.session_state.thumbs_resultado = ("warning", clase, confianza, "No se reconoció el gesto claramente. Toma otra foto.")
        else:
            acierto = (usuario_dice_correcto == preg["correcta"])
            mensaje = actualizar_puntaje(acierto)
            publicar_feedback(acierto)  # Buzzer + LED instantáneos en Wokwi
            st.session_state.thumbs_resultado = ("ok" if acierto else "error", clase, confianza, mensaje)

if st.session_state.thumbs_resultado:
    estado, clase, confianza, mensaje = st.session_state.thumbs_resultado
    st.write(f"Predicción: **{clase}** (confianza: {confianza:.0%})")
    if estado == "ok":
        st.success(mensaje)
    elif estado == "error":
        st.error(mensaje)
    else:
        st.warning(mensaje)

if st.button("Siguiente pregunta ➡️", use_container_width=True):
    avanzar_pregunta()
    st.rerun()
