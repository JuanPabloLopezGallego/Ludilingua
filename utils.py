import streamlit as st
import paho.mqtt.client as mqtt
import threading
import queue
import numpy as np
from io import BytesIO
import wave

# --- Configuración MQTT ---
BROKER = "broker.emqx.io"
PORT = 1883
TOPIC_BOTON = "ludilingua_pro_2026/boton"
TOPIC_FEEDBACK = "ludilingua_pro_2026/feedback"

mqtt_queue = queue.Queue()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker MQTT")
        client.subscribe(TOPIC_BOTON)
        print(f"Suscrito a {TOPIC_BOTON}")
    else:
        print(f"Error de conexión MQTT, código: {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"DEBUG: Mensaje MQTT recibido en {msg.topic}: {payload}")
    mqtt_queue.put((msg.topic, payload))

@st.cache_resource
def get_mqtt_client():
    # Client ID FIJO para mantener la sesión y la suscripción vivas
    client_id = "StreamlitLudiLingua_001"
    client = mqtt.Client(client_id=client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    thread = threading.Thread(target=client.loop_forever, daemon=True)
    thread.start()
    return client

mqtt_client = get_mqtt_client()

def publicar_feedback(acierto: bool):
    mensaje = "CORRECTO" if acierto else "INCORRECTO"
    mqtt_client.publish(TOPIC_FEEDBACK, mensaje)
    print(f"DEBUG: Publicado feedback en {TOPIC_FEEDBACK}: {mensaje}")

def obtener_ultimo_mensaje_boton():
    try:
        ultimo = None
        while not mqtt_queue.empty():
            topic, payload = mqtt_queue.get_nowait()
            print(f"DEBUG: Procesando mensaje de {topic}: {payload}")
            if topic == TOPIC_BOTON:
                ultimo = payload
        return ultimo
    except queue.Empty:
        return None

# --- Funciones de Puntaje y Sonido (sin cambios) ---
def inicializar_sesion():
    if "score" not in st.session_state:
        st.session_state.score = 0

def actualizar_puntaje(acierto: bool):
    if acierto:
        st.session_state.score += 10
        return "Correcto! +10 puntos"
    else:
        st.session_state.score -= 5
        return "Incorrecto. -5 puntos"

def mostrar_puntaje():
    st.markdown(
        f"""
        <div style="background-color:#ffffff; padding:15px; border-radius:15px; text-align:center; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;">
            <h2 style="margin:0; color:#333;">Puntaje: <span style="color:#2e7d32;">{st.session_state.score}</span></h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

def generar_sonido(frecuencia: int, duracion: float = 0.3) -> bytes:
    sample_rate = 44100
    t = np.linspace(0, duracion, int(sample_rate * duracion), endpoint=False)
    onda = 0.5 * np.sin(2 * np.pi * frecuencia * t)
    audio = (onda * 32767).astype(np.int16)
    buffer = BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    return buffer.getvalue()

def reproducir_feedback(acierto: bool):
    if acierto:
        st.audio(generar_sonido(1000), format="audio/wav")
        st.markdown("<div style='text-align:center; font-size: 30px;'>LED Verde encendido!</div>", unsafe_allow_html=True)
    else:
        st.audio(generar_sonido(300), format="audio/wav")
        st.markdown("<div style='text-align:center; font-size: 30px;'>LED Rojo encendido!</div>", unsafe_allow_html=True)
