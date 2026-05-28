import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import io
from streamlit_mic_recorder import speech_to_text

# IMPORTAR EL ROBOT DESDE EL OTRO ARCHIVO
from robot_compras import agregar_producto_fester

# Configuración de la página web
st.set_page_config(page_title="Fester AI", layout="wide")

# --- FUNCIÓN DE VOZ AUTOMÁTICA ---
def reproducir_voz(texto):
    try:
        # Limpiar formatos para que el lector no deletree los asteriscos o guiones
        texto_limpio = texto.replace('*', '').replace('-', ' ').replace('#', '')
        tts = gTTS(text=texto_limpio, lang='es', tld='com.mx')
        archivo_audio = io.BytesIO()
        tts.write_to_fp(archivo_audio)
        st.audio(archivo_audio.getvalue(), format='audio/mp3', autoplay=True)
    except Exception as e:
        st.error(f"Error reproduciendo audio: {e}")

# --- INICIALIZAR LA MEMORIA EN LA SESIÓN ---
if "historial_pantalla" not in st.session_state:
    st.session_state.historial_pantalla = []
    
if "chat_ia" not in st.session_state:
    st.session_state.chat_ia = None

# Extraer de forma segura la API Key desde la Bóveda de Secretos de Streamlit
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None
    st.sidebar.error("⚠️ Configura la GEMINI_API_KEY en los Secrets de Streamlit Cloud.")

# Conectar e inicializar el modelo de Gemini con sus reglas fijas
if api_key and st.session_state.chat_ia is None:
    try:
        genai.configure(api_key=api_key)
        
        instrucciones_sistema = """
        Eres un ingeniero experto en soporte técnico de la marca Fester.
        ¡IMPORTANTE! Tienes una integración especial que te permite agregar productos al carrito de compras del usuario automáticamente.
        
        FLUJO OBLIGATORIO:
        1. En tu primer mensaje tras ver la foto, saluda y haz una breve observación. Luego pregunta obligatoriamente: "¿Este proyecto lo realizarás tú mismo como usuario DIY o eres un contratista profesional?".
        2. Adapta tu respuesta según su perfil (sencillo para DIY, avanzado y estructural para profesionales).
        3. Si el usuario te pide comprar, agregar al carrito o adquirir el producto, SÓLO dile: "¡Excelente decisión! Enseguida el sistema automático agregará el producto a tu carrito de compras". NUNCA lo mandes a buscar un distribuidor físico ni a una ferretería.
        
        REGLAS DE ESTILO:
        - Tus respuestas serán leídas en voz alta. Sé conversacional, fluido y ve al grano.
        - EVITA por completo usar listas con viñetas o asteriscos para que el lector de voz suene natural.
        """
        
        modelo = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=instrucciones_sistema
        )
        st.session_state.chat_ia = modelo.start_chat(history=[])
    except Exception as e:
        st.sidebar.error(f"Error al conectar con Gemini: {e}")

# --- BARRA LATERAL (ENTRADA DE IMÁGENES) ---
st.sidebar.header("Evidencia Visual")
foto_camara = st.sidebar.camera_input("Tomar Foto")
foto_subida = st.sidebar.file_uploader("O cargar archivo", type=['jpg', 'jpeg', 'png'])
foto_final = foto_camara if foto_camara else foto_subida

if foto_final:
    st.sidebar.image(foto_final, caption="Superficie cargada", use_container_width=True)

# --- PANEL PRINCIPAL ---
st.title("🏗️ Fester AI: Asistente Inteligente")
st.write("Soporte de ingeniería y soluciones de impermeabilización instantáneas.")

# Botón para iniciar el flujo con la foto
if foto_final and st.sidebar.button("🔍 Iniciar Análisis Visual"):
    if not st.session_state.chat_ia:
        st.sidebar.error("⚠️ El cerebro de la IA no está listo. Revisa la configuración de tu API Key.")
    else:
        imagen = Image.open(foto_final)
        imagen.thumbnail((800, 800))
        
        with st.spinner("Analizando superficie..."):
            try:
                respuesta = st.session_state.chat_ia.send_message([imagen, "Hola, te comparto la foto de la superficie afectada para comenzar."])
                st.session_state.historial_pantalla.append({"rol": "usuario", "texto": "*(Imagen enviada para análisis)*"})
                st.session_state.historial_pantalla.append({"rol": "ia", "texto": respuesta.text})
                reproducir_voz(respuesta.text)
            except Exception as e:
                st.error(f"Error analizando la imagen: {e}")

# Dibujar el historial de conversación en la pantalla
for mensaje in st.session_state.historial_pantalla:
    with st.chat_message("user" if mensaje["rol"] == "usuario" else "assistant"):
        st.markdown(mensaje["texto"])

# --- CONTROLES DE ENTRADA (VOZ Y TEXTO) ---
st.write("---")
col_mic, col_text = st.columns([1, 4])

with col_mic:
    texto_hablado = speech_to_text(language='es-MX', start_prompt="🎙️ Hablar", stop_prompt="🛑 Detener", just_once=True, key='mic')

with col_text:
    texto_escrito = st.chat_input("Escribe aquí tu duda o respuesta...")

# Seleccionar la entrada que contenga datos
nueva_pregunta = texto_hablado if texto_hablado else texto_escrito

if nueva_pregunta:
    if not st.session_state.chat_ia:
        st.error("⚠️ El asistente no está conectado. Revisa la clave de acceso.")
    else:
        # Registrar y mostrar la duda del usuario
        with st.chat_message("user"):
            st.markdown(nueva_pregunta)
        st.session_state.historial_pantalla.append({"rol": "usuario", "texto": nueva_pregunta})
        
        with st.spinner("Procesando..."):
            try:
                # --- DETECTOR AUTOMÁTICO DEL ROBOT ---
                texto_minusculas = nueva_pregunta.lower()
                if "comprar" in texto_minusculas or "carrito" in texto_minusculas:
                    st.toast("Activando brazo robótico en segundo plano...", icon="🤖")
                    
                    # Ejecutar el robot de navegación
                    resultado_robot = agregar_producto_fester("Impermeabilizante")
                    
                    st.session_state.historial_pantalla.append({"rol": "ia", "texto": f"*(Acción automática)*: {resultado_robot}"})
                    with st.chat_message("assistant"):
                        st.success(resultado_robot)
                # -------------------------------------

                # Obtener la respuesta de la IA
                respuesta = st.session_state.chat_ia.send_message(nueva_pregunta)
                
                with st.chat_message("assistant"):
                    st.markdown(respuesta.text)
                st.session_state.historial_pantalla.append({"rol": "ia", "texto": respuesta.text})
                
                # Leer en voz alta
                reproducir_voz(respuesta.text)
                
            except Exception as e:
                st.error(f"Error procesando la solicitud: {e}")
