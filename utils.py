import random
import threading
import uuid

import paho.mqtt.client as mqtt
import streamlit as st

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_BOTON = "ludilingua_pro_2026/boton"
TOPIC_FEEDBACK = "ludilingua_pro_2026/feedback"


# =====================================================================
#  🎨 HELPERS DE DISEÑO (CSS puro, sin Lottie)
# =====================================================================
def inject_global_css():
    """Tipografía, botones, alertas, inputs y audio corregidos."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Baloo+2:wght@400;600;700;800&display=swap');

        .stApp, .stApp * { font-family: 'Fredoka', sans-serif; }
        .main .block-container { max-width: 1100px; padding-top: 1.5rem; }

        /* ---------- Botones grandes y divertidos ---------- */
        .stButton > button {
            background: linear-gradient(135deg, #ff6b9d 0%, #c77dff 100%);
            color: #fff !important;
            border: none;
            border-radius: 50px;
            padding: 0.9rem 2rem;
            font-size: 1.15rem;
            font-weight: 700;
            font-family: 'Baloo 2', sans-serif;
            letter-spacing: 0.5px;
            transition: all 0.25s cubic-bezier(.34,1.56,.64,1);
            box-shadow: 0 6px 0 rgba(0,0,0,0.18);
        }
        .stButton > button:hover {
            transform: translateY(-4px) scale(1.03);
            box-shadow: 0 10px 0 rgba(0,0,0,0.2);
        }
        .stButton > button:active {
            transform: translateY(2px);
            box-shadow: 0 3px 0 rgba(0,0,0,0.15);
        }

        /* ---------- Alertas personalizadas ---------- */
        .kid-alert {
            padding: 1.2rem 1.6rem;
            border-radius: 24px;
            font-size: 1.1rem;
            font-weight: 600;
            font-family: 'Baloo 2', sans-serif;
            margin: 1rem 0;
            display: flex;
            align-items: center;
            gap: 0.9rem;
            animation: alertSlide 0.45s cubic-bezier(.34,1.56,.64,1);
            border: 3px solid #fff;
        }
        .kid-alert .a-icon { font-size: 2rem; animation: iconPulse 1.4s ease-in-out infinite; }
        .kid-success { background: linear-gradient(135deg, #b8f2c8 0%, #7fdfa0 100%); color: #0d5c2a; box-shadow: 0 8px 24px rgba(45,206,137,0.4); }
        .kid-error   { background: linear-gradient(135deg, #ffb3ba 0%, #ff8a9a 100%); color: #7a1024; box-shadow: 0 8px 24px rgba(255,107,129,0.4); }
        .kid-info    { background: linear-gradient(135deg, #c9e7ff 0%, #a8d4ff 100%); color: #0a3d70; box-shadow: 0 8px 24px rgba(90,160,255,0.4); }
        .kid-warn    { background: linear-gradient(135deg, #fff3b0 0%, #ffe066 100%); color: #6b4e00; box-shadow: 0 8px 24px rgba(255,200,50,0.4); }
        @keyframes alertSlide {
            from { opacity: 0; transform: translateX(-30px) scale(0.9); }
            to   { opacity: 1; transform: translateX(0) scale(1); }
        }
        @keyframes iconPulse {
            0%, 100% { transform: scale(1) rotate(0deg); }
            50%      { transform: scale(1.2) rotate(10deg); }
        }

        /* ---------- Banner del botón de Wokwi ---------- */
        .wokwi-banner {
            display: inline-flex;
            align-items: center;
            gap: 0.7rem;
            background: rgba(255,255,255,0.85);
            backdrop-filter: blur(10px);
            padding: 0.7rem 1.4rem;
            border-radius: 30px;
            border: 3px dashed #ff6b9d;
            font-family: 'Baloo 2', sans-serif;
            font-weight: 700;
            color: #4a1c40;
            font-size: 1rem;
            margin: 0.5rem auto;
            animation: bannerFloat 2s ease-in-out infinite;
        }
        .wokwi-banner .w-icon { font-size: 1.6rem; animation: iconPulse 1.5s ease-in-out infinite; }
        @keyframes bannerFloat {
            0%, 100% { transform: translateY(0); }
            50%      { transform: translateY(-5px); }
        }

        /* ---------- Labels de widgets ---------- */
        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label,
        .stTextInput > label,
        .stTextInput label p,
        .stTextInput label,
        .stCameraInput > label,
        .stCameraInput label p,
        .stCameraInput label {
            color: #1a1a2e !important;
            text-shadow:
                0 0 4px rgba(255,255,255,0.95),
                0 0 8px rgba(255,255,255,0.75),
                1px 1px 3px rgba(255,255,255,0.95) !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            opacity: 1 !important;
        }

        /* ---------- Input ---------- */
        .stTextInput > div > div > input {
            border-radius: 20px !important;
            border: 3px solid #fff !important;
            padding: 1rem 1.4rem !important;
            font-size: 1.2rem !important;
            font-family: 'Fredoka', sans-serif !important;
            box-shadow: 0 4px 14px rgba(0,0,0,0.12) !important;
            color: #1a1a2e !important;
            background: #ffffff !important;
        }
        .stTextInput > div > div > input::placeholder { color: #9aa0b4 !important; }
        .stTextInput > div > div > input:focus {
            border-color: #ffd166 !important;
            box-shadow: 0 0 0 4px rgba(255,209,102,0.35) !important;
        }

        /* ---------- Reproductor de audio nativo ---------- */
        [data-testid="stAudio"] {
            background: #ffffff !important;
            border-radius: 20px !important;
            padding: 10px !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15) !important;
            border: 3px solid #fff !important;
            margin: 1rem auto !important;
            max-width: 500px !important;
        }
        [data-testid="stAudio"] audio {
            width: 100%;
            color-scheme: light !important;
            border-radius: 10px;
        }

        /* ---------- Cámara ---------- */
        [data-testid="stCameraInput"] {
            border: 5px solid #fff;
            border-radius: 26px;
            padding: 0.8rem;
            background: #fff;
            box-shadow: 0 12px 32px rgba(0,0,0,0.15);
            margin: 1rem 0;
        }

        /* ---------- Responsive ---------- */
        @media (max-width: 768px) {
            .float-emoji { font-size: 2rem !important; opacity: 0.28 !important; }
            .stButton > button { font-size: 1rem !important; padding: 0.8rem 1.5rem !important; }
        }
    </style>
    """, unsafe_allow_html=True)


def animated_bg(c1, c2, c3, speed=15):
    st.markdown(f"""
    <style>
        .stApp {{
            background: linear-gradient(-45deg, {c1}, {c2}, {c3}, {c1});
            background-size: 400% 400%;
            animation: bgShift {speed}s ease infinite;
        }}
        @keyframes bgShift {{
            0%   {{ background-position: 0% 50%; }}
            50%  {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
    </style>
    """, unsafe_allow_html=True)


def floating_emojis(emojis):
    """Emojis flotantes repartidos por toda la pantalla de forma simétrica."""
    spans = "".join(f'<span class="float-emoji">{e}</span>' for e in emojis)
    st.markdown(f"""
    <style>
        .emoji-cloud {{
            position: fixed !important;
            inset: 0 !important; /* 🔧 FIX: Ocupa exactamente el 100% visible, ignorando el scroll */
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }}
        .float-emoji {{
            position: absolute;
            font-size: 3.5rem;
            opacity: 0.35;
            animation: emojiBounce 1.5s ease-in-out infinite;
            will-change: transform;
        }}
        /* Distribución simétrica en los laterales y esquinas */
        .float-emoji:nth-child(1) {{ top: 8%;  left: 4%; }}
        .float-emoji:nth-child(2) {{ top: 15%; right: 4%; }}
        .float-emoji:nth-child(3) {{ bottom: 15%; left: 6%; }}
        .float-emoji:nth-child(4) {{ bottom: 10%; right: 6%; }}
        .float-emoji:nth-child(5) {{ top: 45%; left: 2%; }}
        .float-emoji:nth-child(6) {{ top: 55%; right: 2%; }}
        /* Si agregas más de 6 emojis, estos van al centro */
        .float-emoji:nth-child(7) {{ top: 30%; left: 50%; transform: translateX(-50%); }}
        .float-emoji:nth-child(8) {{ bottom: 35%; left: 50%; transform: translateX(-50%); }}
        
        @keyframes emojiBounce {{
            0%, 100% {{ transform: translateY(0) rotate(0deg) scale(1); }}
            50%      {{ transform: translateY(-20px) rotate(10deg) scale(1.1); }}
        }}
    </style>
    <div class="emoji-cloud">{spans}</div>
    """, unsafe_allow_html=True)


def kid_alert(kind, message):
    icons = {"success": "🎉", "error": "😅", "info": "💡", "warn": "⚠️"}
    st.markdown(f"""
    <div class="kid-alert kid-{kind}">
        <span class="a-icon">{icons.get(kind, '💬')}</span>
        <span>{message}</span>
    </div>
    """, unsafe_allow_html=True)


def wokwi_hint(text="Presiona el botón de Wokwi para continuar"):
    st.markdown(f"""
    <div style="text-align:center;">
        <div class="wokwi-banner"><span class="w-icon">🔘</span><span>{text}</span></div>
    </div>
    """, unsafe_allow_html=True)


# =====================================================================
#  📡 MQTT & LÓGICA
# =====================================================================
@st.cache_resource
def get_mqtt():
    estado = {"avances": 0, "lock": threading.Lock()}

    def on_connect(client, userdata, flags, rc, *args):
        client.subscribe(TOPIC_BOTON)

    def on_disconnect(client, userdata, rc, *args):
        pass

    def on_message(client, userdata, msg):
        payload = msg.payload.decode(errors="ignore").strip()
        if msg.topic == TOPIC_BOTON and "AVANZAR" in payload:
            with estado["lock"]:
                estado["avances"] += 1

    client_id = f"streamlit_{uuid.uuid4().hex[:8]}"
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    except AttributeError:
        client = mqtt.Client(client_id=client_id)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=10)
    client.connect_async(BROKER, PORT, 60)
    client.loop_start()
    return client, estado


mqtt_client, estado_mqtt = get_mqtt()


def publicar(topico, mensaje):
    mqtt_client.publish(topico, mensaje)


def publicar_feedback(acierto: bool):
    publicar(TOPIC_FEEDBACK, "CORRECTO" if acierto else "INCORRECTO")


def publicar_limpiar():
    publicar(TOPIC_FEEDBACK, "LIMPIAR")


def hubo_avance_boton(prefijo: str) -> bool:
    clave = f"{prefijo}_avances_vistos"
    actual = estado_mqtt["avances"]
    if clave not in st.session_state:
        st.session_state[clave] = actual
        return False
    if actual != st.session_state[clave]:
        st.session_state[clave] = actual
        return True
    return False


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
    score = st.session_state.get("score", 0)
    st.markdown(f"""
    <div style="text-align:center;">
        <div class="score-card">
            <span class="s-emoji">🏆</span>
            <div>
                <div class="s-label">PUNTOS</div>
                <div class="s-value">{score}</div>
            </div>
            <span class="s-emoji">⭐</span>
        </div>
    </div>
    <style>
        .score-card {{
            display: inline-flex; align-items: center; gap: 1.2rem;
            background: linear-gradient(135deg, #fffbe6 0%, #ffe066 100%);
            border: 4px solid #fff; border-radius: 40px; padding: 0.7rem 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin: 0.6rem auto 1.4rem;
            animation: scoreBounce 2.2s ease-in-out infinite;
        }}
        .s-label {{ font-size: 0.75rem; letter-spacing: 3px; color: #8a6d00; font-weight: 700; font-family: 'Baloo 2', sans-serif; }}
        .s-value {{ font-size: 2.4rem; font-weight: 800; color: #4a3400; line-height: 1; font-family: 'Baloo 2', sans-serif; }}
        .s-emoji {{ font-size: 2rem; animation: wiggleEmoji 1.4s ease-in-out infinite; }}
        @keyframes scoreBounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-6px); }} }}
        @keyframes wiggleEmoji {{ 0%, 100% {{ transform: rotate(0deg); }} 25% {{ transform: rotate(-15deg); }} 75% {{ transform: rotate(15deg); }} }}
    </style>
    """, unsafe_allow_html=True)
