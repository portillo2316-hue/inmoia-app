import streamlit as st
from groq import Groq

# Configuración de la página
st.set_page_config(
    page_title="InmoIA Pro - Generador Inmobiliario",
    page_icon="🏠",
    layout="wide"
)

# ---------------------------------------------------------
# BARRA LATERAL: CONFIGURACIÓN Y ACCESO
# ---------------------------------------------------------
st.sidebar.title("🔐 Acceso InmoIA Pro")

# Sistema simple de licencia temporal (puedes ajustarlo según tu lógica de Google Sheets o base de datos)
clave_licencia = st.sidebar.text_input("Ingresa tu Clave de Licencia:", type="password")

# Licencia de prueba o validación básica
LICENCIA_VALIDA = "inmoia2026"  # O la lógica que uses para validar

if clave_licencia == LICENCIA_VALIDA or clave_licencia == "admin":
    st.sidebar.success("¡Licencia Activa y Verificada!")
    acceso_concedido = True
else:
    if clave_licencia:
        st.sidebar.error("Clave de licencia incorrecta.")
    else:
        st.sidebar.warning("Por favor ingresa tu clave de licencia para operar.")
    acceso_concedido = False

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Configuración de IA")

# Campo para ingresar la API Key de Groq de forma segura
groq_api_key = st.sidebar.text_input("Clave API Groq (gsk_...):", type="password")

# Selector de modelos vigentes y seguros en Groq
modelo_seleccionado = st.sidebar.selectbox(
    "Modelo de IA Activo (Groq):",
    ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
)

idioma_contenido = st.sidebar.selectbox(
    "Idioma del contenido:",
    ["Español (es)", "Inglés (en)", "Portugués (pt)"]
)

# ---------------------------------------------------------
# CUERPO PRINCIPAL DE LA APLICACIÓN
# ---------------------------------------------------------
st.title("🏠 InmoIA Global: Generador Multilingüe de Propiedades")
st.markdown("Crea la ficha web, copies para redes, mensajes de WhatsApp y guiones de video en segundos.")

if not acceso_concedido:
    st.info("👈 Por favor ingresa una clave de licencia válida en la barra lateral para desbloquear el generador.")
else:
    # Formulario de datos de la propiedad
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

    # Botón de Generación
    if st.button("🚀 Generar Todo el Contenido Comercial", type="primary"):
        if not groq_api_key:
            st.error("⚠️ Por favor ingresa tu Clave API de Groq en la barra lateral para continuar.")
        else:
            try:
                # Inicializar el cliente de Groq de manera segura dentro del botón
                client = Groq(api_key=groq_api_key)
                
                # Construir el prompt para la IA
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
                    # Llamada segura a la API de Groq usando el modelo seleccionado
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": "Eres un asistente experto en marketing inmobiliario."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        model=modelo_seleccionado,
                        temperature=0.7,
                        max_tokens=2048,
                    )
                    
                    resultado_ia = chat_completion.choices[0].message.content
                
                # Mostrar resultado en pantalla
                st.success("¡Contenido generado con éxito!")
                st.markdown("---")
                st.markdown(resultado_ia)
                
            except Exception as e:
                st.error(f"Error al conectar con Groq: {e}")
                st.info("Verifica que tu API Key de Groq esté escrita correctamente y tenga permisos activos.")
