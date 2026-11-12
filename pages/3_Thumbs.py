import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import random
from streamlit_autorefresh import st_autorefresh
from utils import (inicializar_sesion, actualizar_puntaje, mostrar_puntaje,
                   publicar_feedback, reproducir_feedback, boton_avanzar_presionado)

st.set_page_config(page_title="Thumbs Up/Down", page_icon="👍", layout="centered")
st_autorefresh(interval=3500, key="mqtt_refresh_thumbs")
inicializar_sesion()

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
    h1, h2, h3, p { color: #4a1c40 !important; }
    .emoji-header { text-align: center; font-size: 80px; }
</style>
""", unsafe_allow_html=True)

st.title("👍 Pulgar Arriba / Abajo")

@st.cache_resource(show_spinner="Cargando modelo IA...")
def cargar_modelo():
    try:
        model = tf.keras.models.load_model("assets/thumbs_up.h5", compile=False)
        with open("assets/labels.txt", "r") as f:
            labels = [line.strip() for line in f.readlines() if line.strip()]
        return model, labels
    except Exception as e:
        print(f"Error modelo: {e}")
        return None, None

model, labels = cargar_modelo()
if model is None:
    st.error("Error al cargar el modelo. Asegúrate de tener 'thumbs_up.h5' y 'labels.txt' en assets/.")
    st.stop()

preguntas = [
    {"espanol": "vaca", "ingles": "cow", "correcta": True},
    {"espanol": "perro", "ingles": "cat", "correcta": False},
    {"espanol": "sol", "ingles": "sun", "correcta": True},
    {"espanol": "libro", "ingles": "table", "correcta": False},
]

def nueva_pregunta():
    actual = st.session_state.pregunta_actual
    opciones = [p for p in preguntas if p != actual]
    st.session_state.pregunta_actual = random.choice(opciones) if opciones else random.choice(preguntas)
    st.session_state.thumbs_round += 1
    st.session_state.thumbs_procesado = None

if "pregunta_actual" not in st.session_state:
    st.session_state.pregunta_actual = random.choice(preguntas)
if "thumbs_round" not in st.session_state:
    st.session_state.thumbs_round = 0
if "thumbs_procesado" not in st.session_state:
    st.session_state.thumbs_procesado = None

if boton_avanzar_presionado():
    nueva_pregunta()
    st.toast("🔘 ¡Botón físico! Siguiente pregunta.", icon="⏭️")
    st.rerun()

preg = st.session_state.pregunta_actual

st.markdown("<div class='emoji-header'>👍 / 👎</div>", unsafe_allow_html=True)
st.markdown(f"### La traducción de **{preg['espanol']}** es **{preg['ingles']}**?")
st.markdown("Muestra **pulgar arriba 👍** si es correcto, o **pulgar abajo 👎** si es incorrecto.")
st.info("💡 Puedes presionar el botón físico de Wokwi en cualquier momento para saltar.")

mostrar_puntaje()

img_file = st.camera_input("Muestra tu pulgar a la cámara", key=f"cam_{st.session_state.thumbs_round}")

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
    st.image(image, caption="Tu captura", use_container_width=True)

    file_id = getattr(img_file, "file_id", str(img_file.size))
    clave = f"{file_id}|{preg['espanol']}_{preg['ingles']}|{st.session_state.thumbs_round}"

    if st.session_state.thumbs_procesado != clave:
        data = preprocesar_imagen(image)
        prediction = model.predict(data, verbose=0)
        clase_idx = int(np.argmax(prediction))
        clase = labels[clase_idx]
        confianza = float(prediction[0][clase_idx])

        clase_low = clase.lower()
        if "background" in clase_low or "nothing" in clase_low or "none" in clase_low or "neutral" in clase_low:
            st.warning(f"No se reconoció gesto claro ({clase} {confianza:.2f}). Intenta de nuevo.")
            st.stop()

        if "up" in clase_low or "arriba" in clase_low or "bueno" in clase_low or "correct" in clase_low or "1" in clase_low:
            # Ajusta según tu labels.txt, por defecto Teachable: 0 up, 1 down
            usuario_dice_correcto = True if "down" not in clase_low and "abajo" not in clase_low else False
            # Lógica simple: si contiene up -> True
            if "up" in clase_low or "arriba" in clase_low:
                usuario_dice_correcto = True
            else:
                usuario_dice_correcto = True
        elif "down" in clase_low or "abajo" in clase_low:
            usuario_dice_correcto = False
        else:
            # Si tus labels son "0 ..." "1 ..." asumimos 0=up, 1=down
            usuario_dice_correcto = (clase_idx == 0)

        acierto = (usuario_dice_correcto == preg["correcta"])
        mensaje = actualizar_puntaje(acierto)
        publicar_feedback(acierto)
        reproducir_feedback(acierto)

        st.session_state.thumbs_procesado = clave
        st.session_state.thumbs_clase = clase
        st.session_state.thumbs_conf = confianza
        st.session_state.thumbs_acierto = acierto
        st.session_state.thumbs_mensaje = mensaje
    else:
        clase = st.session_state.thumbs_clase
        confianza = st.session_state.thumbs_conf
        acierto = st.session_state.thumbs_acierto
        mensaje = st.session_state.thumbs_mensaje

    st.write(f"Predicción: **{clase}** (confianza: {confianza:.2f})")
    if acierto:
        st.success(mensaje + " LED verde en Wokwi 🟢")
    else:
        st.error(mensaje + " LED rojo en Wokwi 🔴")

    if st.button("Siguiente pregunta ⏭️"):
        nueva_pregunta()
        st.rerun()
