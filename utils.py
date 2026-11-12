import streamlit as st
import numpy as np
from io import BytesIO
import wave

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
        st.markdown("<div style='text-align:center; font-size: 30px; animation: fadeIn 1s;'>🟢 <b>¡LED Verde encendido!</b></div>", unsafe_allow_html=True)
    else:
        st.audio(generar_sonido(300), format="audio/wav")
        st.markdown("<div style='text-align:center; font-size: 30px; animation: fadeIn 1s;'>🔴 <b>¡LED Rojo encendido!</b></div>", unsafe_allow_html=True)
