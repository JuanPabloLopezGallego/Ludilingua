import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import random
from streamlit_autorefresh import st_autorefresh
from utils import (inicializar_sesion, actualizar_puntaje, mostrar_puntaje,
                   publicar_feedback, reproducir_feedback, boton_avanzar_presionado)

st.set_page_config(page_title="Thumbs Up/Down", page_icon="👍", layout="centered")
st_autorefresh(interval=3500, key="mqtt_refresh_thumbs")aimport streamlit as st
import tensorflow as tf
import numpy as np
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


@st.cache_resource
def cargar_modelo():
    try:
        model = tf.keras.models.load_model("assets/thumbs_up.h5")
        with open("assets/labels.txt", "r") as f:
            labels = [line.strip() for line in f.readlines()]
        return model, labels
    except Exception:
        return None, None


def preprocesar_imagen(img: Image.Image) -> np.ndarray:
    image = ImageOps.fit(img, (224, 224), Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized = (image_array.astype(np.float32) / 127.0) - 1
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized
    return data


# Botón físico -> siguiente pregunta
if hubo_avance_boton(P):
    reiniciar_ronda(P, PREGUNTAS)
    st.toast("🔘 Botón de Wokwi: siguiente pregunta")

if f"{P}_actual" not in st.session_state:
    reiniciar_ronda(P, PREGUNTAS)

model, labels = cargar_modelo()
if model is None:
    st.error("Error al cargar el modelo. Asegúrate de tener 'thumbs_up.h5' y 'labels.txt' en assets/.")
    st.stop()

preg = st.session_state[f"{P}_actual"]
ronda = st.session_state[f"{P}_ronda"]
intento = st.session_state[f"{P}_intento"]
respondido = st.session_state[f"{P}_respondido"]

st.markdown("<div class='emoji-header'>👍 / 👎</div>", unsafe_allow_html=True)
st.markdown(f"### ¿La traducción de **{preg['espanol']}** es **{preg['ingles']}**?")
st.markdown("Muestra **pulgar arriba** si es correcto, o **pulgar abajo** si es incorrecto.")
mostrar_puntaje()

img_file = st.camera_input(
    "Muestra tu pulgar a la cámara",
    key=f"{P}_cam_{ronda}_{intento}",
)

if img_file is not None:
    image = Image.open(img_file).convert("RGB")
    st.image(image, width=250)

    # Evaluar UNA sola vez por intento
    if not respondido:
        prediction = model.predict(preprocesar_imagen(image), verbose=0)
        idx = int(np.argmax(prediction))
        clase = labels[idx]
        confianza = float(prediction[0][idx])

        c = clase.lower()
        if "up" in c or "arriba" in c:
            gesto = True
        elif "down" in c or "abajo" in c:
            gesto = False
        else:
            gesto = None

        if gesto is None:
            resultado = {"acierto": None,
                         "mensaje": "No se reconoció el gesto. Intenta de nuevo.",
                         "clase": clase, "conf": confianza}
        else:
            acierto = gesto == preg["correcta"]
            mensaje = actualizar_puntaje(acierto)
            publicar_feedback(acierto)
            resultado = {"acierto": acierto, "mensaje": mensaje,
                         "clase": clase, "conf": confianza}

        st.session_state[f"{P}_resultado"] = resultado
        st.session_state[f"{P}_respondido"] = True

resultado = st.session_state[f"{P}_resultado"]
if resultado:
    st.write(f"Predicción: **{resultado['clase']}** (confianza: {resultado['conf']:.2f})")
    if resultado["acierto"] is None:
        st.warning(resultado["mensaje"])
    elif resultado["acierto"]:
        st.success(resultado["mensaje"])
    else:
        st.error(resultado["mensaje"])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔁 Intentar de nuevo"):
            reintentar(P)
            st.rerun()
    with c2:
        if st.button("➡️ Siguiente pregunta"):
            reiniciar_ronda(P, PREGUNTAS)
            st.rerun()
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
