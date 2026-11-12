import streamlit as st
import paho.mqtt.client as mqtt
import threading
import queue
import json
import time

# --- Configuración MQTT ---
BROKER = "broker.emqx.io"
PORT = 1883
TOPIC_BOTON = "ludilingua/boton"
TOPIC_FEEDBACK = "ludilingua/feedback"

# Cola global para recibir mensajes del hilo de MQTT
if "mqtt_queue" not in st.session_state:
    st.session_state.mqtt_queue = queue.Queue()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker MQTT")
        client.subscribe(TOPIC_BOTON)
    else:
        print(f"Error de conexión MQTT, código: {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Mensaje MQTT recibido en {msg.topic}: {payload}")
    # Enviamos el mensaje a la cola para que Streamlit lo procese
    st.session_state.mqtt_queue.put((msg.topic, payload))

@st.cache_resource
def get_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    # Iniciamos el loop en un hilo separado
    thread = threading.Thread(target=client.loop_forever, daemon=True)
    thread.start()
    return client

# Inicializamos el cliente al cargar el módulo
mqtt_client = get_mqtt_client()

def publicar_feedback(acierto: bool):
    """Publica en el broker para que Wokwi encienda el LED y suene el buzzer."""
    mensaje = "CORRECTO" if acierto else "INCORRECTO"
    mqtt_client.publish(TOPIC_FEEDBACK, mensaje)

def obtener_ultimo_mensaje_boton():
    """Revisa si hay mensajes nuevos del botón en la cola."""
    try:
        # Vacia la cola y devuelve el último mensaje si es del tópico del botón
        ultimo = None
        while not st.session_state.mqtt_queue.empty():
            topic, payload = st.session_state.mqtt_queue.get_nowait()
            if topic == TOPIC_BOTON:
                ultimo = payload
        return ultimo
    except queue.Empty:
        return None

# --- Funciones de Puntaje (sin cambios) ---
def inicializar_sesion():
    if "score" not in st.session_state:
        st.session_state.score = 0

def actualizar_puntaje(acierto: bool):
    if acierto:
        st.session_state.score += 10
        return "✅ ¡Correcto! +10 puntos"
    else:
        st.session_state.score -= 5
        return "❌ Incorrecto. -5 puntos"

def mostrar_puntaje():
    st.markdown(
        f"""
        <div style="background-color:#ffffff; padding:15px; border-radius:15px; text-align:center; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;">
            <h2 style="margin:0; color:#333;">🏆 Puntaje: <span style="color:#2e7d32;">{st.session_state.score}</span></h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
