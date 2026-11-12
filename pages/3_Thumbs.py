import os
import numpy as np
import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
from streamlit_autorefresh import st_autorefresh
from utils import (inicializar_sesion, actualizar_puntaje, mostrar_puntaje,
                   publicar_feedback, reiniciar_ronda, hubo_avance_boton,
                   inject_global_css, animated_bg, floating_emojis,
                   kid_alert, wokwi_hint)

P = "thumbs"
PREGUNTAS = [
    {"espanol":"vaca","ingles":"cow","correcta":True},
    {"espanol":"perro","ingles":"cat","correcta":False},
    {"espanol":"sol","ingles":"sun","correcta":True},
    {"espanol":"libro","ingles":"table","correcta":False},
    {"espanol":"gato","ingles":"cat","correcta":True},
    {"espanol":"casa","ingles":"house","correcta":True},
    {"espanol":"coche","ingles":"car","correcta":True},
    {"espanol":"árbol","ingles":"dog","correcta":False},
    {"espanol":"luna","ingles":"moon","correcta":True},
    {"espanol":"estrella","ingles":"star","correcta":True},
    {"espanol":"mesa","ingles":"chair","correcta":False},
    {"espanol":"silla","ingles":"chair","correcta":True},
    {"espanol":"agua","ingles":"fire","correcta":False},
    {"espanol":"fuego","ingles":"water","correcta":False},
    {"espanol":"tierra","ingles":"earth","correcta":True},
    {"espanol":"viento","ingles":"wind","correcta":True},
    {"espanol":"manzana","ingles":"apple","correcta":True},
    {"espanol":"plátano","ingles":"banana","correcta":True},
    {"espanol":"naranja","ingles":"orange","correcta":True},
    {"espanol":"uva","ingles":"grape","correcta":True},
    {"espanol":"elefante","ingles":"elephant","correcta":True},
    {"espanol":"león","ingles":"lion","correcta":True},
    {"espanol":"tigre","ingles":"tiger","correcta":True},
    {"espanol":"mono","ingles":"monkey","correcta":True},
    {"espanol":"jirafa","ingles":"zebra","correcta":False},
    {"espanol":"computadora","ingles":"computer","correcta":True},
    {"espanol":"teléfono","ingles":"phone","correcta":True},
    {"espanol":"música","ingles":"music","correcta":True},
    {"espanol":"guitarra","ingles":"piano","correcta":False},
    {"espanol":"piano","ingles":"piano","correcta":True},
    {"espanol":"escuela","ingles":"school","correcta":True},
    {"espanol":"maestro","ingles":"student","correcta":False},
    {"espanol":"estudiante","ingles":"student","correcta":True},
    {"espanol":"médico","ingles":"doctor","correcta":True},
    {"espanol":"enfermera","ingles":"nurse","correcta":True},
]

st.set_page_config(page_title="Thumbs Up/Down", page_icon="👍", layout="centered")
inject_global_css()
animated_bg("#ffd166", "#ff9e7d", "#ff6b9d", speed=14)
floating_emojis(["🌞","⭐","🌟","👍","👎","🌻"])
st_autorefresh(interval=1000, key="refresh_thumbs")
inicializar_sesion()

st.markdown("""
<style>
    /* 🔧 SOL CENTRADO — inset: -100vmax lo hace 100vmax más grande que el viewport por todos lados,
       así su centro cae exactamente en el centro del viewport y jamás se descentra al rotar. */
    .stApp::before {
        content: "";
        position: fixed !important;
        inset: -100vmax !important;
        pointer-events: none;
        background: repeating-conic-gradient(
            from 0deg at 50% 50%,
            rgba(255,220,80,0.15) 0deg 15deg,
            transparent 15deg 30deg
        );
        animation: sunSpin 60s linear infinite;
        z-index: 0;
    }
    @keyframes sunSpin {
        from { transform: rotate(0deg); }
        to   { transform: rotate(360deg); }
    }

    .thumbs-title { text-align: center; font-family: 'Baloo 2', sans-serif; font-weight: 800; font-size: clamp(1.8rem, 4.5vw, 3.2rem); color: #fff; text-shadow: 3px 3px 0 #d97706, 6px 6px 22px rgba(0,0,0,0.35); margin: 0.3rem 0 0.2rem; animation: titlePop 2s ease-in-out infinite; }
    @keyframes titlePop { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.04); } }

    .thumbs-badge { text-align: center; font-size: 5.5rem; animation: thumbsShake 1.6s ease-in-out infinite; filter: drop-shadow(0 0 22px rgba(255,209,102,0.9)); margin: 0.4rem 0; }
    @keyframes thumbsShake { 0%, 100% { transform: rotate(-8deg); } 50% { transform: rotate(8deg); } }

    .question-card { background: rgba(255,255,255,0.9); backdrop-filter: blur(12px); border-radius: 32px; padding: 2rem 1.5rem; text-align: center; margin: 1rem auto; max-width: 95%; box-shadow: 0 15px 40px rgba(0,0,0,0.18); border: 5px solid #fff; animation: questionBounce 3s ease-in-out infinite; position: relative; z-index: 1; }
    @keyframes questionBounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }

    .question-card h2 { font-family: 'Baloo 2', sans-serif; font-weight: 800; font-size: clamp(1.2rem, 3.5vw, 2rem); color: #4a1c40; margin: 0; line-height: 1.3; }
    .question-card .big-word { color: #ff4d94; background: linear-gradient(90deg,#ff4d94,#ffb84d,#ff4d94); background-size: 200% auto; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; animation: wordShift 3s linear infinite; }
    @keyframes wordShift { 0% { background-position: 0% 50%; } 100% { background-position: 200% 50%; } }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="thumbs-title">👍 ¿Correcto o Incorrecto? 👎</h1>', unsafe_allow_html=True)
st.markdown('<div class="thumbs-badge">👍 / 👎</div>', unsafe_allow_html=True)

@st.cache_resource(show_spinner="Cargando modelo IA...")
def cargar_modelo():
    model_path = "thumbs_up.h5"
    labels_path = "labels.txt"
    if not os.path.exists(model_path):
        return None, f"❌ No se encuentra el archivo: {model_path}"
    if not os.path.exists(labels_path):
        return None, f"❌ No se encuentra el archivo: {labels_path}"
    try:
        model = tf.keras.models.load_model(model_path, compile=False)
        with open(labels_path, "r") as f:
            labels = [l.strip() for l in f.readlines() if l.strip()]
        return model, labels
    except Exception as e:
        return None, f"❌ Error al cargar Keras: {str(e)}"

def preprocesar_imagen(img: Image.Image) -> np.ndarray:
    size = (224, 224)
    image = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
    arr = np.asarray(image)
    normalized = (arr.astype(np.float32) / 127.0) - 1
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized
    return data

if hubo_avance_boton(P):
    reiniciar_ronda(P, PREGUNTAS)
    st.toast("🔘 ¡Siguiente pregunta!", icon="
