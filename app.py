import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import io
from streamlit_mic_recorder import speech_to_text

# Configuración de la página
st.set_page_config(page_title="Fester AI", layout="wide")

# --- FUNCIÓN DE VOZ ---
def reproducir_voz(texto):
    try:
        # Genera el audio en español con acento de México (com.mx)
        # Eliminamos caracteres especiales comunes para mejorar la lectura de voz
        texto_limpio = texto.replace('*', '').replace('-', ' ').replace('#', '')
        tts = gTTS(text=texto_limpio, lang='es', tld='com.mx')
        archivo_audio = io.BytesIO()
        tts.write_to_fp(archivo_audio)
        st.audio(archivo_audio.getvalue(), format='audio/mp3', autoplay=True)
    except Exception as e:
        st.error(f"Error reproducriendo audio: {e}")

# --- BARRA LATERAL (CONFIGURACIÓN Y FOTOS) ---
st.sidebar.header("1. Configuración")
api_key = st.sidebar.text_input("Pega aquí tu API Key:", type="password")

st.sidebar.header("2. Evidencia Visual")
foto_camara = st.sidebar.camera_input("Cámara")
foto_subida = st.sidebar.file_uploader("O sube foto", type=['jpg', 'jpeg', 'png'])
foto_final = foto_camara if foto_camara else foto_subida

if foto_final:
    st.sidebar.image(foto_final, caption="Superficie a analizar", use_container_width=True)

# --- INICIALIZAR LA MEMORIA (CEREBRO) ---
if "historial_pantalla" not in st.session_state:
    st.session_state.historial_pantalla = []
    
if "chat_ia" not in st.session_state:
    st.session_state.chat_ia = None

# Encender el motor con Instrucciones del Sistema obligatorias
if api_key and st.session_state.chat_ia is None:
    try:
        genai.configure(api_key=api_key)
        
        # --- AQUÍ ESTÁ LA MAGIA DEL COMPORTAMIENTO ---
        instrucciones_sistema = """
        Eres un ingeniero experto en soporte técnico de la marca de impermeabilizantes Fester. Tu misión es diagnosticar problemas de humedad y guiar al usuario.
        
        FLUJO OBLIGATORIO DE CONVERSACIÓN (SÍGUELO PASO A PASO):
        1. En tu primerísimo mensaje (cuando el usuario te envíe la foto), NO debes dar un diagnóstico detallado, ni dar pasos, ni recomendar productos todavía. Saluda amigablemente, menciona de forma súper breve y general qué tipo de daño observas en la foto (ej. desprendimiento de pintura o marcas de humedad) y hazle obligatoriamente esta pregunta exacta: "¿Este proyecto lo realizarás tú mismo como usuario DIY (Hazlo tú mismo) o eres un contratista o aplicador profesional?".
        
        2. Una vez que el usuario te responda si es DIY o profesional, analiza la foto que te mandó al inicio y entrega el diagnóstico y solución adaptados 100% a su perfil:
           - Si te dice que es DIY: Usa un tono muy sencillo, empático, explicaciones cortas y directas, sin tecnicismos pesados. Recomienda soluciones de la línea Fester que sean fáciles, seguras y listas para aplicar por cualquier persona en casa (como la línea Fester Imperfácil o selladores acrílicos sencillos).
           - Si te dice que es Profesional: Usa un tono de ingeniería, técnico, preciso y avanzado. Explica la preparación estructural profunda de la superficie (como remoción total, lavado por presión, etc.) y recomienda productos Fester de alto rendimiento o grado industrial (como Fester CR-66, Vaportite, morteros Festergrout, etc.).
        
        REGLAS DE ESTILO PARA AUDIO:
        - Tus respuestas serán leídas en voz alta. Sé siempre conversacional, fluido y ve al grano.
        - EVITA por completo usar asteriscos, guiones, tablas o viñetas largas. Estructura tus textos en párrafos naturales y limpios para que el sintetizador de voz no suene extraño.
        """
        
        modelo = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=instrucciones_sistema
        )
        st.session_state.chat_ia = modelo.start_chat(history=[])
    except Exception as e:
        st.sidebar.error(f"Error al conectar el cerebro: {e}")

# --- ÁREA PRINCIPAL (EL CHAT) ---
st.title("Chalancito")
st.write("Tu asistente técnico adaptado a tu nivel de experiencia.")

# Análisis de la foto inicial
if foto_final and st.sidebar.button("🔍 Iniciar Análisis Visual"):
    if not st.session_state.chat_ia:
        st.sidebar.error("⚠️ Pon tu API Key primero.")
    else:
        imagen = Image.open(foto_final)
        imagen.thumbnail((800, 800))
        
        with st.spinner("Revisando evidencia visual..."):
            try:
                # Le mandamos la imagen con un detonador simple. La instrucción del sistema hará que pregunte el perfil.
                respuesta = st.session_state.chat_ia.send_message([imagen, "Hola, te comparto la foto de la superficie afectada para comenzar."])
                st.session_state.historial_pantalla.append({"rol": "usuario", "texto": "*(Imagen enviada para análisis)*"})
                st.session_state.historial_pantalla.append({"rol": "ia", "texto": respuesta.text})
                
                reproducir_voz(respuesta.text)
            except Exception as e:
                st.error(f"Error: {e}")

# Dibujar el historial
for mensaje in st.session_state.historial_pantalla:
    if mensaje["rol"] == "usuario":
        with st.chat_message("user"):
            st.markdown(mensaje["texto"])
    else:
        with st.chat_message("assistant"):
            st.markdown(mensaje["texto"])

# --- ZONA DE ENTRADA (VOZ Y TEXTO) ---
st.write("---")
col_mic, col_text = st.columns([1, 4])

with col_mic:
    texto_hablado = speech_to_text(
        language='es-MX',
        start_prompt="🎙️ Hablar",
        stop_prompt="🛑 Detener",
        just_once=True,
        key='microfono'
    )

with col_text:
    texto_escrito = st.chat_input("Escribe tu respuesta o duda aquí...")

nueva_pregunta = texto_hablado if texto_hablado else texto_escrito

if nueva_pregunta:
    if not st.session_state.chat_ia:
        st.error("⚠️ Pon tu API Key en el menú de la izquierda para empezar.")
    else:
        with st.chat_message("user"):
            st.markdown(nueva_pregunta)
        st.session_state.historial_pantalla.append({"rol": "usuario", "texto": nueva_pregunta})
        
        with st.spinner("Procesando..."):
            try:
                respuesta = st.session_state.chat_ia.send_message(nueva_pregunta)
                
                with st.chat_message("assistant"):
                    st.markdown(respuesta.text)
                st.session_state.historial_pantalla.append({"rol": "ia", "texto": respuesta.text})
                
                reproducir_voz(respuesta.text)
                
            except Exception as e:
                st.error(f"Error: {e}")