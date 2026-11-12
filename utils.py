import random
import threading
import uuid

import paho.mqtt.client as mqtt
import streamlit as st

BROKER = "broker.hivemq.com"          # MISMO broker que el ESP32
PORT = 1883
TOPIC_BOTON = "ludilingua_pro_2026/boton"
TOPIC_FEEDBACK = "ludilingua_pro_2026/feedback"


@st.cache_resource
def get_mqtt():
    """Un único cliente MQTT para toda la app."""
    estado = {"avances": 0, "lock": threading.Lock()}

    def on_connect(client, userdata, flags, rc, *args):
        print("MQTT conectado. Suscribiendo a", TOPIC_BOTON)
        client.subscribe(TOPIC_BOTON)

    def on_message(client, userdata, msg):
        payload = msg.payload.decode(errors="ignore").strip()
        print(f"DEBUG MQTT: {msg.topic} -> {payload}")
        if msg.topic == TOPIC_BOTON and "AVANZAR" in payload:
            with estado["lock"]:
                estado["avances"] += 1

    client_id = f"streamlit_{uuid.uuid4().hex[:8]}"
    try:
        # paho-mqtt 2.x
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    except AttributeError:
        # paho-mqtt 1.x
        client = mqtt.Client(client_id=client_id)

    client.on_connect = on_connect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=10)
    client.connect_async(BROKER, PORT, 60)
    client.loop_start()
    return client, estado


mqtt_client, estado_mqtt = get_mqtt()


# ---------------- MQTT ----------------
def publicar(topico, mensaje):
    mqtt_client.publish(topico, mensaje)
    print(f"DEBUG: publicado en {topico}: {mensaje}")


def publicar_feedback(acierto: bool):
    publicar(TOPIC_FEEDBACK, "CORRECTO" if acierto else "INCORRECTO")


def publicar_limpiar():
    publicar(TOPIC_FEEDBACK, "LIMPIAR")


def hubo_avance_boton(prefijo: str) -> bool:
    """True solo una vez por cada pulsación del botón físico."""
    clave = f"{prefijo}_avances_vistos"
    actual = estado_mqtt["avances"]
    if clave not in st.session_state:
        st.session_state[clave] = actual
        return False
    if actual != st.session_state[clave]:
        st.session_state[clave] = actual
        return True
    return False


# ---------------- Rondas ----------------
def reiniciar_ronda(prefijo: str, opciones: list):
    st.session_state[f"{prefijo}_actual"] = random.choice(opciones)
    st.session_state[f"{prefijo}_ronda"] = st.session_state.get(f"{prefijo}_ronda", 0) + 1
    st.session_state[f"{prefijo}_intento"] = 0
    st.session_state[f"{prefijo}_respondido"] = False
    st.session_state[f"{prefijo}_resultado"] = None
    publicar_limpiar()


def reintentar(prefijo: str):
    st.session_state[f"{prefijo}_intento"] += 1
    st.session_state[f"{prefijo}_respondido"] = False
    st.session_state[f"{prefijo}_resultado"] = None
    publicar_limpiar()


def normalizar(texto: str) -> str:
    return texto.lower().strip().strip(".,!?¿¡")


# ---------------- Puntaje ----------------
def inicializar_sesion():
    if "score" not in st.session_state:
        st.session_state.score = 0


def actualizar_puntaje(acierto: bool):
    if acierto:
        st.session_state.score += 10
        return "¡Correcto! +10 puntos"
    st.session_state.score -= 5
    return "Incorrecto. -5 puntos"


def mostrar_puntaje():
    st.markdown(
        f"""
        <div style="background-color:#ffffff; padding:15px; border-radius:15px; text-align:center;
                    box-shadow: 0px 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;">
            <h2 style="margin:0; color:#333;">Puntaje: <span style="color:#2e7d32;">{st.session_state.score}</span></h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
