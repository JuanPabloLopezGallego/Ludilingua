import streamlit as st
import paho.mqtt.client as mqtt
import queue
import uuid
import random

MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_PORT = 1883
TOPIC_FEEDBACK = "ludilingua_pro_2026/feedback"
TOPIC_BOTON = "ludilingua_pro_2026/boton"


class MQTTManager:
    """Mantiene una única conexión MQTT viva en segundo plano para toda la app."""
    def __init__(self):
        self.button_queue = queue.Queue()
        self.connected = False
        client_id = f"LudilinguaStreamlit-{uuid.uuid4().hex[:8]}"

        # Compatible con paho-mqtt 1.x y 2.x
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
            self.client.on_connect = self._on_connect_v2
        except AttributeError:
            self.client = mqtt.Client(client_id=client_id)
            self.client.on_connect = self._on_connect_v1

        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        try:
            self.client.connect_async(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"Error iniciando MQTT: {e}")

    def _on_connect_v1(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            client.subscribe(TOPIC_BOTON, qos=1)

    def _on_connect_v2(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self.connected = True
            client.subscribe(TOPIC_BOTON, qos=1)

    def _on_disconnect(self, *args):
        self.connected = False

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8", errors="ignore").strip()
        if payload.startswith("AVANZAR"):
            # Guardamos el evento en la cola para no perder ni un clic
            self.button_queue.put(payload)

    def publish_feedback(self, acierto: bool):
        mensaje = "CORRECTO" if acierto else "INCORRECTO"
        self.client.publish(TOPIC_FEEDBACK, mensaje, qos=1, retain=False)

    def check_button_pressed(self) -> bool:
        """Devuelve True si hubo al menos una pulsación pendiente y limpia la cola."""
        pressed = False
        while not self.button_queue.empty():
            try:
                self.button_queue.get_nowait()
                pressed = True
            except queue.Empty:
                break
        return pressed


@st.cache_resource
def get_mqtt_manager() -> MQTTManager:
    return MQTTManager()


def inicializar_sesion():
    # Asegura que el cliente MQTT en segundo plano arranque desde el primer segundo
    get_mqtt_manager()
    if "puntaje" not in st.session_state:
        st.session_state.puntaje = 0
    if "racha" not in st.session_state:
        st.session_state.racha = 0


def actualizar_puntaje(acierto: bool) -> str:
    inicializar_sesion()
    if acierto:
        st.session_state.puntaje += 10
        st.session_state.racha += 1
        return f"🎉 ¡Excelente! Respuesta correcta (+10 pts | 🔥 Racha: {st.session_state.racha})"
    else:
        st.session_state.racha = 0
        return "❌ Respuesta incorrecta. ¡No te rindas!"


def mostrar_puntaje():
    mqtt_mgr = get_mqtt_manager()
    estado_iot = "🟢 Wokwi Link Activo" if mqtt_mgr.connected else "🟡 Conectando MQTT..."
    col1, col2, col3 = st.columns(3)
    col1.metric("⭐ Puntaje", st.session_state.get("puntaje", 0))
    col2.metric("🔥 Racha", st.session_state.get("racha", 0))
    col3.caption(estado_iot)


def publicar_feedback(acierto: bool):
    mqtt_mgr = get_mqtt_manager()
    mqtt_mgr.publish_feedback(acierto)


def obtener_ultimo_mensaje_boton() -> str:
    mqtt_mgr = get_mqtt_manager()
    if mqtt_mgr.check_button_pressed():
        return "AVANZAR"
    return ""


def elegir_siguiente_item(lista: list, actual):
    """Garantiza que al avanzar SIEMPRE cambie a una palabra/pregunta diferente."""
    if len(lista) <= 1:
        return lista[0]
    opciones = [item for item in lista if item != actual]
    return random.choice(opciones)
