import streamlit as st
from google import genai
import time

# Configuración inicial de la página
st.set_page_config(
    page_title="InmoIA Pro - Generador Inmobiliario con IA",
    page_icon="🏠",
    layout="wide"
)

# ---------------------------------------------------------
# GESTIÓN DE PARÁMETROS URL
# ---------------------------------------------------------
query_params = st.query_params
url_access = query_params.get("access", "")

# ---------------------------------------------------------
# BARRA LATERAL: ACCESO, PRECIO Y MÉTODOS DE PAGO
# ---------------------------------------------------------
st.sidebar.title("🔐 Acceso Clientes")

clave_licencia = st.sidebar.text_input("Clave de Licencia:", type="password", value=url_access)
licencias_validas = ["inmoia2026", "inmo2026", "admin"]

if clave_licencia.strip().lower() in licencias_validas or url_access:
    st.sidebar.success("¡Licencia Activa y Verificada!")
    acceso_concedido = True
else:
    acceso_concedido = False
    if clave_licencia:
        st.sidebar.error("Licencia incorrecta.")
    else:
        st.sidebar.warning("Ingresa tu licencia o adquiere tu acceso.")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("💳 Suscripción InmoIA Pro")
    st.sidebar.markdown("""
    * **Valor mensual:** `$50.000 COP`
    * **Métodos habilitados:** Nequi, PSE, Tarjetas
    """)
    
    st.sidebar.markdown(
        """
        <a href="https://mpago.li/tutu-link-de-ejemplo" target="_blank">
            <div style="display: flex; align-items: center; justify-content: center; background-color: #009EE3; color: white; padding: 10px 15px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px;">
                💳 Pagar con PSE / Mercado Pago
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("📱 **Pago por Nequi (`3164142727`):** Escríbenos al WhatsApp con tu comprobante para entregarte tu clave manual.")
    st.sidebar.markdown(
        """
        <a href="https://wa.me/573164142727?text=Hola,%20pagué%20por%20Nequi,%20quiero%20mi%20clave%20de%20InmoIA%20Pro" target="_blank">
            <div style="display: flex; align-items: center; justify-content: center; background-color: #25D366; color: white; padding: 8px 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 13px;">
                💬 Soporte Nequi WhatsApp
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Configuración IA")
gemini_api_key = st.sidebar.text_input("Clave API Gemini:", type="password")
idioma_contenido = st.sidebar.selectbox("Idioma de salida:", ["Español", "Inglés", "Portugués"])

# ---------------------------------------------------------
# CUERPO PRINCIPAL (LANDING PAGE PÚBLICA)
# ---------------------------------------------------------
st.title("🏠 InmoIA Pro: El Superpoder de las Inmobiliarias con Inteligencia Artificial")
st.markdown("### Multiplica tus ventas creando descripciones persuasivas, copies para redes y guiones de video en segundos.")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown("✨ **Fichas Web Persuasivas**")
    st.caption("Redactadas por expertos para enamorar a los compradores desde el primer párrafo.")
with col_b:
    st.markdown("📱 **Redes Sociales & WhatsApp**")
    st.caption("Copies listos para Instagram, Facebook y chats de ventas con un solo clic.")
with col_c:
    st.markdown("🎬 **Guiones para Reels / TikTok**")
    st.caption("Estructuras de video diseñadas para captar la atención de inmediato.")

st.markdown("---")

# ---------------------------------------------------------
# ZONA PROTEGIDA
# ---------------------------------------------------------
if not acceso_concedido:
    st.info("💡 **Vista previa bloqueada.** Adquiere tu suscripción con el botón azul de Mercado Pago o ingresa tu clave de licencia en la barra lateral para desbloquear el generador.")
    
    with st.expander("👀 Ver ejemplo de lo que genera InmoIA Pro"):
        st.markdown("""
        * **Ficha Web:** *Espectacular apartamento moderno en Medellín con vista panorámica...*
        * **WhatsApp:** *¡Oportunidad única! Apartamento de 90m² con piscina y seguridad 24/7...*
        * **Reel/TikTok:** *[Gancho de 3 segundos] ¿Buscas el hogar de sueños en la mejor zona? Mira esto...*
        """)
else:
    st.success("🚀 ¡Bienvenido al panel operativo de InmoIA Pro! Configura los datos de tu inmueble abajo:")
    
    col1, col2 = st.columns(2)
    with col1:
        tipo_propiedad = st.selectbox("Tipo de Inmueble", ["Apartamento", "Casa", "Local Comercial", "Oficina", "Lote / Terreno"])
        precio_moneda = st.text_input("Precio y Moneda", "220.000 USD")
        ubicacion = st.text_input("Ubicación (Ciudad / Barrio)", "Medellín")
        
    with col2:
        area = st.text_input("Área construida", "90 m²")
        garajes = st.text_input("Estacionamiento / Garajes", "2 parqueaderos")
        habitaciones_banos = st.text_input("Habitaciones y Baños", "3 habitaciones, 2 baños")

    detalles_adicionales = st.text_area("Detalles adicionales / Amenidades:", "Piscina, seguridad 24/7, vista panorámica, excelente iluminación natural.")

    if st.button("🚀 Generar Todo el Contenido Comercial", type="primary"):
        if not gemini_api_key:
            st.error("⚠️ Por favor ingresa tu Clave API de Gemini en la barra lateral para continuar.")
        else:
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

            # Intento con reintento automático si hay alta demanda (503)
            exito = False
            resultado_ia = ""
            client = genai.Client(api_key=gemini_api_key.strip())
            
            with st.spinner("Conectando con la inteligencia artificial de Gemini..."):
                for intento in range(2):
                    try:
                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=prompt,
                        )
                        resultado_ia = response.text
                        exito = True
                        break
                    except Exception as e:
                        if "503" in str(e) and intento == 0:
                            time.sleep(2) # Espera 2 segundos y reintenta
                            continue
                        else:
                            error_msg = str(e)

            if exito:
                st.success("¡Contenido generado con éxito!")
                st.markdown("---")
                st.markdown(resultado_ia)
            else:
                st.error(f"Error temporal por alta demanda en los servidores de la IA: {error_msg}")
                st.info("Por favor, vuelve a hacer clic en el botón de generar en unos segundos.")
