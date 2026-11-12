import streamlit as st
import numpy as np
from io import BytesIO
import wave

def inicializar_sesion():
    """Inicializa el puntaje en el estado de sesión si no existe."""
    if "score" not in st.session_state:
        st.session_state.score = 0

def actualizar_puntaje(acierto: bool):
    """Suma o resta puntos y retorna el mensaje de feedback."""
    if acierto:
        st.session_state.score += 10
        return "✅ ¡Correcto! +10 puntos"
    else:
        st.session_state.score -= 5
        return "❌ Incorrecto. -5 puntos"

def mostrar_puntaje():
    """Muestra el puntaje actual en un badge llamativo."""
    st.markdown(
        f"""
        <div style="background-color:#f0f2f6; padding:10px; border-radius:10px; text-align:center;">
            <h3 style="margin:0;">🏆 Puntaje: <span style="color:#2e7d32;">{st.session_state.score}</span></h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

def generar_sonido(frecuencia: int, duracion: float = 0.3) -> bytes:
    """Genera un tono simple en formato WAV (para feedback auditivo)."""
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
    """Reproduce sonido y muestra LED simulado."""
    if acierto:
        st.audio(generar_sonido(1000), format="audio/wav")
        st.markdown("🟢 **LED Verde encendido**")
    else:
        st.audio(generar_sonido(300), format="audio/wav")
        st.markdown("🔴 **LED Rojo encendido**")

def cargar_lottie(filepath: str):
    """Carga una animación Lottie desde un archivo local."""
    import json
    with open(filepath, "r") as f:
        return json.load(f)
