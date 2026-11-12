import streamlit as st
import paho.mqtt.client as mqtt
import queue
import numpy as np
from io import BytesIO
import wave

# --- Configuración MQTT UNIFICADA ---
BROKER = "broker.emqx.io"
PORT = 1883
TOPIC_BOTON = "ludilingua_pro_2026/boton"
TOPIC_FEEDBACK = "ludilingua_pro_2026/feedback"

mqtt_queue = queue.Queue()

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Conectado al broker MQTT")
        client.subscribe(TOPIC_BOTON, qos=1)
        print(f"Suscrito a {TOPIC_BOTON}")
    else:
        print(f"Error de conexión MQTT, código: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode().strip()
        print(f"DEBUG MQTT {msg.topic}: {payload}")
        mqtt_queue.put((msg.topic, payload))
    except Exception as e:
        print(f"Error on_message: {e}")

@st.cache_resource(show_spinner=False)
def get_mqtt_client():
    try:
        # paho-mqtt >= 2.0
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="StreamlitLudiLingua_001")
    except Exception:
        # paho-mqtt < 2.0
        client = mqtt.Client(client_id="StreamlitLudiLingua_001")

    client.on_connect = on_connect
    client.on_message = on_message
    client.reconnect_delay_set(1, 10)
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        print("MQTT loop iniciado")
    except Exception as e:
        print(f"Error conectando MQTT: {e}")
    return client

mqtt_client = get_mqtt_client()

def publicar_feedback(acierto: bool):
    try:
        mensaje = "CORRECTO" if acierto else "INCORRECTO"
        mqtt_client.publish(TOPIC_FEEDBACK, mensaje, qos=1)
        print(f"DEBUG Publicado en {TOPIC_FEEDBACK}: {mensaje}")
    except Exception as e:
        print(f"Error publicando feedback: {e}")

def obtener_ultimo_mensaje_boton():
    ultimo = None
    while True:
        try:
            topic, payload = mqtt_queue.get_nowait()
            if topic == TOPIC_BOTON and "AVANZAR" in payload:
                ultimo = payload
        except queue.Empty:
            break
    return ultimo

def boton_avanzar_presionado() -> bool:
    """Devuelve True UNA sola vez por cada pulsación física."""
    return obtener_ultimo_mensaje_boton() is not None

# --- Puntaje ---
def inicializar_sesion():
    if "score" not in st.session_state:
        st.session_state.score = 0

def actualizar_puntaje(acierto: bool):
    if acierto:
        st.session_state.score += 10
        return "¡Correcto! +10 puntos 🎉"
    else:
        st.session_state.score = max(0, st.session_state.score - 5)
        return "Incorrecto. -5 puntos 😅"

def mostrar_puntaje():
    inicializar_sesion()
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
    # Sonido local en el navegador (además del buzzer físico)
    if acierto:
        st.audio(generar_sonido(1000), format="audio/wav")
    else:
        st.audio(generar_sonido(300), format="audio/wav")
