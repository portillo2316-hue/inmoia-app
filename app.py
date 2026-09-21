import streamlit as st
from google import genai
import time

# Configuración inicial de la página
st.set_page_config(
    page_title="InmoIA Pro - Global Real Estate AI",
    page_icon="🏠",
    layout="wide"
)

# ---------------------------------------------------------
# GESTIÓN DE PARÁMETROS URL (Para auto-acceso tras pago)
# ---------------------------------------------------------
query_params = st.query_params
url_access = query_params.get("access", "")

# ---------------------------------------------------------
# BARRA LATERAL: ACCESO, PRECIO Y MÉTODOS DE PAGO
# ---------------------------------------------------------
st.sidebar.title("🔐 Acceso Clientes / Global")

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
    * **Valor mensual:** `$50.000 COP` / `15 USD`
    * **Métodos habilitados:** Nequi, PSE, Tarjetas (Global)
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
st.sidebar.subheader("⚙️ Configuración IA Global")
gemini_api_key = st.sidebar.text_input("Clave API Gemini:", type="password")

idioma_contenido = st.sidebar.selectbox(
    "🌍 Idioma del Contenido:", 
    ["Español", "English (Inglés)", "Português (Portugués)", "Français (Francés)", "Deutsch (Alemán)", "Italiano"]
)

# ---------------------------------------------------------
# CUERPO PRINCIPAL (LANDING PAGE PÚBLICA)
# ---------------------------------------------------------
st.title("🏠 InmoIA Pro: El Superpoder Global para Inmobiliarias con IA")
st.markdown("### Multiplica tus ventas creando descripciones persuasivas, copies para redes y guiones de video en segundos y en cualquier idioma.")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown("✨ **Fichas Web Persuasivas**")
    st.caption("Redactadas por expertos para enamorar compradores internacionales.")
with col_b:
    st.markdown("📱 **Redes Sociales & WhatsApp**")
    st.caption("Copies listos para Instagram, Facebook y chats globales.")
with col_c:
    st.markdown("🎬 **Guiones para Reels / TikTok**")
    st.caption("Estructuras de video diseñadas para captar atención masiva.")

st.markdown("---")

with st.expander("🚀 Conoce todo lo que incluye InmoIA Pro (Funciones Globales)"):
    st.markdown("""
    * 🎯 **Personalización Automática:** Adaptación al perfil del cliente (familias, inversores globales, jóvenes).
    * 🌍 **Multilingüe Real:** Genera contenido nativo adaptado a los mercados de América, Europa y más.
    * 📱 **Respuestas Rápidas para WhatsApp:** Sugerencias automáticas de textos para cerrar ventas en chats.
    """)

# ---------------------------------------------------------
# ZONA PROTEGIDA
# ---------------------------------------------------------
if not acceso_concedido:
    st.info("💡 **Vista previa bloqueada.** Adquiere tu suscripción o ingresa tu clave de licencia en la barra lateral para desbloquear el generador global.")
    
    with st.expander("👀 Ver ejemplo de lo que genera InmoIA Pro"):
        st.markdown("""
        * **Ficha Web:** *Espectacular apartamento moderno con vista panorámica...*
        * **WhatsApp:** *¡Oportunidad única! Apartamento de 90m² con piscina...*
        * **Reel/TikTok:** *[Gancho global] ¿Buscas el hogar de tus sueños? Mira esto...*
        """)
else:
    st.success("🚀 ¡Bienvenido al panel operativo global de InmoIA Pro! Configura los datos de tu inmueble:")
    
    col1, col2 = st.columns(2)
    with col1:
        tipo_propiedad = st.selectbox("Tipo de Inmueble", ["Apartamento / Apartment", "Casa / House", "Local Comercial / Commercial", "Oficina / Office", "Lote / Land"])
        precio_moneda = st.text_input("Precio y Moneda", "220.000 USD")
        ubicacion = st.text_input("Ubicación (Ciudad / País)", "Miami / Medellín")
        perfil_cliente = st.selectbox("🎯 Perfil del Cliente Objetivo", ["Familias", "Inversionistas Globales", "Jóvenes profesionales", "Expatriados / Turistas"])
        
    with col2:
        area = st.text_input("Área construida", "90 m²")
        garajes = st.text_input("Estacionamiento / Garajes", "2 parqueaderos")
        habitaciones_banos = st.text_input("Habitaciones y Baños", "3 habitaciones, 2 baños")
        tono_comercial = st.selectbox("🗣️ Tono del Copy", ["Persuasivo y Emocional", "Corporativo y Elegante", "Urgente / Alta Conversión"])

    detalles_adicionales = st.text_area("Detalles adicionales / Amenidades:", "Piscina, seguridad 24/7, vista panorámica, excelente iluminación natural.")

    if st.button("🚀 Generar Contenido Comercial Global", type="primary"):
        if not gemini_api_key:
            st.error("⚠️ Por favor ingresa tu Clave API de Gemini en la barra lateral para continuar.")
        else:
            prompt = f"""
            Actúa como un experto copywriter inmobiliario internacional y especialista en marketing digital global.
            Genera contenido comercial persuasivo y profesional adaptado estrictamente al siguiente idioma de salida: {idioma_contenido}.
            
            Datos del inmueble:
            - Tipo: {tipo_propiedad}
            - Ubicación: {ubicacion}
            - Precio: {precio_moneda}
            - Área: {area}
            - Distribución: {habitaciones_banos}
            - Estacionamiento: {garajes}
            - Amenidades y detalles: {detalles_adicionales}
            - Perfil del Comprador Objetivo: {perfil_cliente}
            - Tono Comercial: {tono_comercial}

            Estructura la respuesta de manera impecable en {idioma_contenido} con las siguientes secciones:
            1. 🏡 **Ficha Técnica & Descripción Web Persuasiva**
            2. 📱 **Copy para Redes Sociales (con hashtags globales)**
            3. 💬 **Mensaje Vendedor para WhatsApp**
            4. 🤖 **Respuestas Rápidas Conversacionales para Chat**
            5. 🎬 **Guion para Reel / TikTok (30 seg)**
            """

            # Modelos estables con doble respaldo automático
            modelos_a_probar = ["gemini-3.8-flash", "gemini-3.6-flash"]
            exito = False
            resultado_ia = ""
            error_msg = ""
            
            client = genai.Client(api_key=gemini_api_key.strip())
            
            with st.spinner(f"Generando contenido global en {idioma_contenido} con IA..."):
                for modelo in modelos_a_probar:
                    for intento in range(2):
                        try:
                            response = client.models.generate_content(
                                model=modelo,
                                contents=prompt,
                            )
                            resultado_ia = response.text
                            exito = True
                            break
                        except Exception as e:
                            error_msg = str(e)
                            if "503" in str(e) and intento == 0:
                                time.sleep(1.5)
                                continue
                            else:
                                break
                    if exito:
                        break

            if exito:
                st.success("¡Contenido global generado con éxito!")
                st.markdown("---")
                st.markdown(resultado_ia)
            else:
                st.error(f"Error al conectar con la IA: {error_msg}")
                st.info("Por favor, vuelve a hacer clic en el botón de generar.")
