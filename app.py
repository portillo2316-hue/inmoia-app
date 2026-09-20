import streamlit as st
from openai import OpenAI
from docx import Document
import io

# -------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA STREAMLIT
# -------------------------------------------------------------------
st.set_page_config(
    page_title="InmoIA - Asistente Inmobiliario Global (Free)",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 InmoIA Global: Generador Multilingüe de Propiedades")
st.caption("Crea la ficha web, copies para redes, mensajes de WhatsApp y guiones de video en segundos de forma 100% GRATUITA.")

# -------------------------------------------------------------------
# BARRA LATERAL: CONFIGURACIÓN Y CREDENCIALES
# -------------------------------------------------------------------
st.sidebar.header("⚙️ Configuración")
api_key = st.sidebar.text_input("Ingresa tu Groq API Key (gsk_...):", type="password")

# Detección dinámica de modelos activos en Groq
modelos_disponibles = []
if api_key:
    try:
        client_temp = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )
        res_models = client_temp.models.list()
        modelos_disponibles = [
            m.id for m in res_models.data 
            if not any(x in m.id.lower() for x in ["whisper", "guard", "safeguard", "embed"])
        ]
    except Exception:
        pass

if not modelos_disponibles:
    modelos_disponibles = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768"
    ]

modelo_ia = st.sidebar.selectbox(
    "🤖 Modelo de IA Activo (Groq):",
    modelos_disponibles
)

idioma = st.sidebar.selectbox(
    "🌐 Idioma del contenido generado:",
    ["Español 🇪🇸", "English 🇺🇸", "Português 🇧🇷"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **InmoIA Free Mode:** Conectado a la API gratuita de Groq Cloud.")

# -------------------------------------------------------------------
# FORMULARIO DE CAPTURA DE DATOS DE LA PROPIEDAD
# -------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Datos Generales")
    tipo_propiedad = st.selectbox("Tipo de Propiedad:", ["Apartamento", "Casa", "Casa Campestre", "Oficina", "Local Comercial", "Terreno / Lote"])
    operacion = st.radio("Tipo de Operación:", ["Venta", "Arriendo / Alquiler"], horizontal=True)
    precio = st.text_input("Precio y Moneda:", placeholder="Ej: $180,000 USD o $2.500.000 COP")
    ubicacion = st.text_input("Ubicación (Ciudad / Barrio):", placeholder="Ej: Zona Norte, El Poblado, Miami Beach")

with col2:
    st.subheader("📐 Especificaciones Técnicas")
    habs = st.number_input("Habitaciones / Dormitorios:", min_value=0, value=3)
    banos = st.number_input("Baños:", min_value=0, value=2)
    area = st.text_input("Área construida (m² o sqft):", placeholder="Ej: 95 m²")
    parqueadero = st.text_input("Estacionamiento / Garajes:", placeholder="Ej: 2 parqueaderos cubiertos")

caracteristicas_extra = st.text_area(
    "🌟 Características Destacadas / Amenidades:",
    placeholder="Ej: Vista panorámica al parque, piscina climatizada, balcón amplio, cocina tipo americana, seguridad 24/7, cerca a centros comerciales..."
)

# -------------------------------------------------------------------
# FUNCIÓN PARA GENERAR DOCUMENTO WORD
# -------------------------------------------------------------------
def crear_word(contenido_dict):
    doc = Document()
    doc.add_heading("Ficha Promocional de Propiedad - InmoIA", level=1)
    
    for titulo, texto in contenido_dict.items():
        doc.add_heading(titulo, level=2)
        doc.add_paragraph(texto)
        doc.add_paragraph()
        
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# -------------------------------------------------------------------
# PROCESAMIENTO
# -------------------------------------------------------------------
if st.button("🚀 Generar Todo el Contenido Comercial"):
    if not api_key:
        st.error("⚠️ Por favor ingresa tu Groq API Key (empieza por gsk_...) en la barra lateral izquierda.")
    elif not precio or not ubicacion:
        st.warning("⚠️ Completa al menos el precio y la ubicación para generar un contenido preciso.")
    else:
        try:
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key
            )
            
            with st.spinner(f"Generando contenido persuasivo usando {modelo_ia}..."):
                prompt = f"""
                Eres un Copywriter Inmobiliario de clase mundial y estratega de marketing digital.
                Genera el contenido comercial para la siguiente propiedad.
                
                DETALLES DE LA PROPIEDAD:
                - Tipo: {tipo_propiedad} en {operacion}
                - Precio: {precio}
                - Ubicación: {ubicacion}
                - Especificaciones: {habs} habitaciones, {banos} baños, Área: {area}, Garajes: {parqueadero}
                - Destacados: {caracteristicas_extra}
                
                IDIOMA REQUERIDO DE SALIDA: {idioma}
                
                Instrucciones de formato obligatorio:
                Organiza tu respuesta usando exactamente estas cuatro secciones con el tag ### como separador:
                
                ### FICHA WEB
                (Escribe una descripción completa, profesional y seductora para portales inmobiliarios. Incluye lista de características.)
                
                ### INSTAGRAM COPY
                (Escribe un post persuasivo con gancho inicial, emojis bien ubicados, llamada a la acción y 8 hashtags estratégicos.)
                
                ### WHATSAPP CLIENTE
                (Escribe un mensaje directo, amigable y estructurado para enviar por WhatsApp a clientes potenciales.)
                
                ### GUION VIDEO
                (Escribe un guion paso a paso de 30 segundos para Reels/TikTok indicando [Escena/Lo que se muestra] y (Voz en off/Lo que se dice).)
                """
                
                response = client.chat.completions.create(
                    model=modelo_ia,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                
                texto_total = response.choices[0].message.content
                
                secciones = texto_total.split("###")
                dict_secciones = {}
                
                for sec in secciones:
                    if sec.strip():
                        lineas = sec.strip().split("\n", 1)
                        titulo_sec = lineas[0].strip()
                        cuerpo_sec = lineas[1].strip() if len(lineas) > 1 else ""
                        dict_secciones[titulo_sec] = cuerpo_sec

                # Guardar en sesión
                st.session_state["resultado_inmo"] = dict_secciones
                st.session_state["nombre_descarga"] = f"InmoIA_{tipo_propiedad}_{ubicacion}.docx"

        except Exception as e:
            st.error(f"Error en la conexión con la API de Groq: {e}")

# -------------------------------------------------------------------
# RENDERIZADO DE RESULTADOS (FUERA DEL BOTÓN)
# -------------------------------------------------------------------
if "resultado_inmo" in st.session_state:
    dict_secciones = st.session_state["resultado_inmo"]
    st.success("¡Contenido comercial generado exitosamente sin costo!")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌐 Ficha Portal Web", 
        "📸 Instagram / Facebook", 
        "💬 WhatsApp Directo", 
        "🎬 Guion TikTok / Reels"
    ])
    
    with tab1:
        st.markdown(dict_secciones.get("FICHA WEB", "No disponible"))
    with tab2:
        st.markdown(dict_secciones.get("INSTAGRAM COPY", "No disponible"))
    with tab3:
        st.markdown(dict_secciones.get("WHATSAPP CLIENTE", "No disponible"))
    with tab4:
        st.markdown(dict_secciones.get("GUION VIDEO", "No disponible"))
    
    st.markdown("---")
    
    buffer_word = crear_word(dict_secciones)
    st.download_button(
        label="📄 Descargar Todo en Documento Word (.docx)",
        data=buffer_word,
        file_name=st.session_state.get("nombre_descarga", "InmoIA_Propiedad.docx"),
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )