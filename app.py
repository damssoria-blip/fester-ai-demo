import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import io
from streamlit_mic_recorder import speech_to_text

# IMPORTAMOS TU ROBOT DE COMPRAS
from robot_compras import agregar_producto_fester

# Configuración de la página
st.set_page_config(page_title="Fester AI", layout="wide")

# --- FUNCIÓN DE VOZ ---
def reproducir_voz(texto):
    try:
        texto_limpio = texto.replace('*', '').replace('-', ' ').replace('#', '')
        tts = gTTS(text=texto_limpio, lang='es', tld='com.mx')
        archivo_audio = io.BytesIO()
        tts.write_to_fp(archivo_audio)
        st.audio(archivo_audio.getvalue(), format='audio/mp3', autoplay=True)
    except Exception as e:
        st.error(f"Error reproduciendo audio: {e}")

# --- INICIALIZAR LA MEMORIA ---
if "historial_pantalla" not in st.session_state:
    st.session_state.historial_pantalla = []
    
if "chat_ia" not in st.session_state:
    st.session_state.chat_ia = None

# Intentar extraer de forma segura la API Key de la Bóveda de Secretos
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None
    st.sidebar.error("⚠️ Falta configurar la GEMINI_API_KEY en los Secrets de Streamlit Cloud.")

# Conectar el modelo con las instrucciones del sistema calibradas
if api_key and st.session_state.chat_ia is None:
    try:
        genai.configure(api_key=api_key)
        
        instrucciones_sistema = """
        Eres un ingeniero experto en soporte técnico de la marca Fester.
        ¡IMPORTANTE! Tienes una integración especial que te permite agregar productos al carrito de compras del usuario automáticamente.
        
        FLUJO OBLIGATORIO:
        1. En tu primer mensaje tras ver la foto, saluda y haz una breve observación. Luego pregunta: "¿Este proyecto lo realizarás tú mismo como usuario DIY o eres un contratista profesional?".
        2. Adapta tu respuesta según su perfil.
        3. Si el usuario te pide comprar, agregar al carrito o adquirir el producto, SÓLO dile: "¡Excelente decisión! Enseguida el sistema automático agregará el producto a tu carrito de compras". NUNCA lo mandes a buscar un distribuidor físico ni a una ferretería.
        
        REGLAS DE ESTILO:
        - Tus respuestas serán leídas en voz alta. Sé conversacional, fluido y ve al grano.
        - EVITA viñetas o listas raras.
        """
        
        modelo = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=instrucciones_sistema
        )
        st.session_state.chat_ia = modelo.start_chat(history=[])
    except Exception as e:
        st.sidebar.error(f"Error al conectar: {e}")

# --- BARRA LATERAL (EVIDENCIA VISUAL) ---
st.sidebar.header("Evidencia Visual")
foto_camara = st.sidebar.camera_input("Cámara")
foto_subida = st.sidebar.file_uploader("O sube foto", type=['jpg', 'jpeg', 'png'])
foto_final = foto_camara if foto_camara else foto_subida

if foto_final:
    st.sidebar.image(foto_final, caption="Superficie a analizar", use_container_width=True)

# --- ÁREA PRINCIPAL (INTERFAZ DE CHAT) ---
st.title("🏗️ Fester AI: Asistente Inteligente")

# Botón detonador para el análisis de imagen inicial
if foto_final and st.sidebar.button("🔍 Iniciar Análisis Visual"):
    if not st.session_state.chat_ia:
        st.sidebar.error("⚠️ El cerebro de la IA no está listo. Revisa tu llave.")
    else:
        imagen = Image.open(foto_final)
        imagen.thumbnail((800, 800))
        
        with st.spinner("Revisando evidencia visual..."):
            try:
                respuesta = st.session_state.chat_ia.send_message([imagen, "Hola, te comparto la foto de la superficie."])
                st.session_state.historial_pantalla.append({"rol": "usuario", "texto": "*(Imagen enviada)*"})
                st.session_state.historial_pantalla.append({"rol": "ia", "texto": respuesta.text})
                reproducir_voz(respuesta.text)
            except Exception as e:
                st.error(f"Error: {e}")

# Mostrar todos los mensajes guardados
for mensaje in st.session_state.historial_pantalla:
    with st.chat_message("user" if mensaje["rol"] == "usuario" else "assistant"):
        st.markdown(mensaje["texto"])

# --- ZONA DE ENTRADA (VOZ Y TEXTO) ---
st.write("---")
col_mic, col_text = st.columns([1, 4])

with col_mic:
    texto_hablado = speech_to_text(language='es-MX', start_prompt="🎙️ Hablar", stop_prompt="🛑 Detener", just_once=True, key='mic')

with col_text:
    texto_escrito = st.chat_input("Escribe tu respuesta o duda aquí...")

nueva_pregunta = texto_hablado if texto_hablado else texto_escrito

if nueva_pregunta:
    if not st.session_state.chat_ia:
        st.error("⚠️ El sistema no está conectado con la IA.")
    else:
        with st.chat_message("user"):
            st.markdown(nueva_pregunta)
        st.session_state.historial_pantalla.append({"rol": "usuario", "texto": nueva_pregunta})
        
        with st.spinner("Procesando..."):
            try:
                # --- GATILLO DINÁMICO DEL ROBOT ---
                texto_minusculas = nueva_pregunta.lower()
                if "comprar" in texto_minusculas or "carrito" in texto_minusculas:
                    st.toast("Activando brazo robótico en segundo plano...", icon="🤖")
                    
                    # Ejecutar el script automático pasándole una búsqueda genérica
                    resultado_robot = agregar_producto_fester("Impermeabilizante")
                    
                    st.session_state.historial_pantalla.append({"rol": "ia", "texto": f"*(Acción automática)*: {resultado_robot}"})
                    with st.chat_message("assistant"):
                        st.success(resultado_robot)
                # ----------------
