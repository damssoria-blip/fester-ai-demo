import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import io
from streamlit_mic_recorder import speech_to_text

# Importar el robot
from robot_compras import agregar_producto_fester

st.set_page_config(page_title="Fester AI", layout="wide")

def reproducir_voz(texto):
    try:
        texto_limpio = texto.replace('*', '').replace('-', ' ').replace('#', '')
        tts = gTTS(text=texto_limpio, lang='es', tld='com.mx')
        archivo_audio = io.BytesIO()
        tts.write_to_fp(archivo_audio)
        st.audio(archivo_audio.getvalue(), format='audio/mp3', autoplay=True)
    except Exception:
        pass

if "historial_pantalla" not in st.session_state:
    st.session_state.historial_pantalla = []
if "chat_ia" not in st.session_state:
    st.session_state.chat_ia = None

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None
    st.sidebar.error("⚠️ Falta configurar la GEMINI_API_KEY en los Secrets.")

if api_key and st.session_state.chat_ia is None:
    genai.configure(api_key=api_key)
    instrucciones_sistema = """
    Eres un ingeniero experto de Fester. 
    1. Primero diagnostica y pregunta si son DIY o Pro.
    2. Si quieren comprar, diles: "¡Excelente decisión! Enseguida el sistema automático agregará el producto a tu carrito de compras."
    3. Responde siempre de forma conversacional para audio, sin usar viñetas.
    """
    modelo = genai.GenerativeModel('gemini-2.5-flash', system_instruction=instrucciones_sistema)
    st.session_state.chat_ia = modelo.start_chat(history=[])

st.sidebar.header("Evidencia Visual")
foto_final = st.sidebar.camera_input("Foto") or st.sidebar.file_uploader("Subir", type=['jpg','png'])

st.title("👷‍♂️ Chalancito")

if foto_final and st.sidebar.button("🔍 Analizar"):
    img = Image.open(foto_final)
    try:
        respuesta = st.session_state.chat_ia.send_message([img, "Analiza esta foto."])
        st.session_state.historial_pantalla.append({"rol": "ia", "texto": respuesta.text})
        reproducir_voz(respuesta.text)
    except Exception as e:
        if "ResourceExhausted" in str(e):
            st.error("⏳ Google nos pide un respiro. Espera 60 segundos antes de volver a preguntar.")
        else:
            st.error(f"Error: {e}")

for m in st.session_state.historial_pantalla:
    with st.chat_message("user" if m["rol"] == "usuario" else "assistant"):
        st.markdown(m["texto"])

st.write("---")
col_mic, col_text = st.columns([1, 4])
with col_mic:
    texto_hablado = speech_to_text(language='es-MX', start_prompt="🎙️ Hablar", stop_prompt="🛑 Detener", key='mic')
texto_escrito = st.chat_input("Escribe aquí...")
nueva_pregunta = texto_hablado if texto_hablado else texto_escrito

if nueva_pregunta:
    st.session_state.historial_pantalla.append({"rol": "usuario", "texto": nueva_pregunta})
    with st.chat_message("user"): 
        st.markdown(nueva_pregunta)
    
    with st.spinner("Procesando..."):
        # Activar el robot si se detecta intención de compra
        texto = nueva_pregunta.lower()
        if "comprar" in texto or "carrito" in texto:
            producto_a_buscar = "Impermeabilizante"
            if "proshield" in texto: producto_a_buscar = "Proshield"
            elif "cr-66" in texto: producto_a_buscar = "CR-66"
            elif "vaportite" in texto: producto_a_buscar = "Vaportite"
            
            st.toast(f"Buscando {producto_a_buscar} en Fester...")
            resultado = agregar_producto_fester(producto_a_buscar)
            st.success(resultado)

        try:
            res = st.session_state.chat_ia.send_message(nueva_pregunta)
            st.session_state.historial_pantalla.append({"rol": "ia", "texto": res.text})
            with st.chat_message("assistant"): 
                st.markdown(res.text)
            reproducir_voz(res.text)
        except Exception as e:
            if "ResourceExhausted" in str(e):
                st.error("⏳ Estás yendo muy rápido. Espera 1 minuto para que se recargue tu cuota gratuita de Google.")
            else:
                st.error(f"Error: {e}")
