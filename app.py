import streamlit as st
from google import genai

st.set_page_config(
    page_title="InmoIA Pro - Generador Inmobiliario",
    page_icon="🏠",
    layout="wide"
)

st.sidebar.title("🔐 Acceso InmoIA Pro")
clave_licencia = st.sidebar.text_input("Ingresa tu Clave de Licencia:", type="password")

licencias_validas = ["inmoia2026", "inmo2026", "admin"]

if clave_licencia.strip().lower() in licencias_validas:
    st.sidebar.success("¡Licencia Activa y Verificada!")
    acceso_concedido = True
else:
    acceso_concedido = False
    if clave_licencia:
        st.sidebar.error("Clave de licencia incorrecta.")
    else:
        st.sidebar.warning("Por favor ingresa tu clave de licencia para operar.")
    st.sidebar.markdown("---")
    st.sidebar.subheader("💳 ¿Adquirir Licencia?")
    st.sidebar.info("Comunícate con soporte para habilitar tu acceso mensual de forma inmediata.")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Configuración de IA")
gemini_api_key = st.sidebar.text_input("Clave API Gemini:", type="password")
idioma_contenido = st.sidebar.selectbox("Idioma del contenido:", ["Español", "Inglés", "Portugués"])

st.title("🏠 InmoIA Global: Generador Multilingüe de Propiedades")
st.markdown("Crea la ficha web, copies para redes, mensajes de WhatsApp y guiones de video en segundos.")

if not acceso_concedido:
    st.info("👈 Por favor ingresa una clave de licencia válida en la barra lateral para desbloquear el generador.")
else:
    col1, col2 = st.columns(2)
    
    with col1:
        tipo_propiedad = st.selectbox("Tipo de Inmueble", ["Apartamento", "Casa", "Local Comercial", "Oficina", "Lote / Terreno"])
        precio_moneda = st.text_input("Precio y Moneda", "220.000 USD")
        ubicacion = st.text_input("Ubicación (Ciudad / Barrio)", "Medellín")
        
    with col2:
        area = st.text_input("Área construida (m² o pies²)", "90 m²")
        garajes = st.text_input("Estacionamiento / Garajes", "2 parqueaderos")
        habitaciones_banos = st.text_input("Habitaciones y Baños", "3 habitaciones, 2 baños")

    detalles_adicionales = st.text_area("Detalles adicionales / Amenidades:", "Piscina, seguridad 24/7, vista panorámica, excelente iluminación natural.")

    if st.button("🚀 Generar Todo el Contenido Comercial", type="primary"):
        if not gemini_api_key:
            st.error("⚠️ Por favor ingresa tu Clave API de Gemini en la barra lateral para continuar.")
        else:
            try:
                client = genai.Client(api_key=gemini_api_key.strip())
                
                prompt = f"""
                Actúa como un experto copywriter inmobiliario y especialista en marketing digital.
                Genera contenido comercial persuasivo y profesional para el siguiente inmueble:
                - Tipo: {tipo_propiedad}
                - Ubicación: {ubicacion}
                - Precio: {precio_moneda}
                - Área: {area}
                - Distribución: {habitaciones_banos}
                - Estacionamiento: {garajes}
                - Amenidades y detalles: {detalles_adicionales}
                - Idioma de salida: {idioma_contenido}

                Estructura la respuesta clara con secciones para:
                1. Ficha Técnica / Descripción Web persuasiva.
                2. Copy para Redes Sociales (Instagram / Facebook con hashtags).
                3. Mensaje corto y vendedor para WhatsApp.
                4. Guion atractivo para un Reel o TikTok de 30 segundos.
                """

                with st.spinner("Generando contenido inmobiliario con inteligencia artificial..."):
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                    )
                    resultado_ia = response.text

                st.success("¡Contenido generado con éxito!")
                st.markdown("---")
                st.markdown(resultado_ia)
                
            except Exception as e:
                st.error(f"Error al conectar con la IA: {e}")
                st.info("Verifica que tu clave API de Gemini sea correcta e intenta de nuevo.")
