import streamlit as st
import docx
from docx import Document
from io import BytesIO
from groq import Groq

# 1. Configuración de la página
st.set_page_config(
    page_title="InmoIA Pro - SaaS Inmobiliario",
    page_icon="🏠",
    layout="wide"
)

# ---------------------------------------------------------
# 2. CONTROL DE ACCESO / MURO DE PAGO (PAYWALL)
# ---------------------------------------------------------
st.sidebar.title("🔐 Acceso InmoIA Pro")

# Lista de claves autorizadas
CLAVES_VALIDAS = ["INMO2026", "PRO-AGENCIA", "CLIENTE1"]

clave = st.sidebar.text_input("Ingresa tu Clave de Licencia:", type="password")

# Si la clave no es válida, la app se bloquea completamente
if clave not in CLAVES_VALIDAS:
    st.title("🔒 InmoIA Pro - Plataforma Restringida")
    st.info("👋 Bienvenida/o a InmoIA. Para acceder al generador de contenido inmobiliario con IA, necesitas una suscripción activa.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚀 ¿Qué puedes hacer con InmoIA Pro?")
        st.markdown("- **Fichas Web:** Descripciones comerciales de alta conversión.")
        st.markdown("- **Redes Sociales:** Copies irresistibles para Instagram, Facebook y TikTok.")
        st.markdown("- **Ventas:** Mensajes persuasivos para WhatsApp y guiones de video.")
        st.markdown("- **Documentos:** Exportación directa a Microsoft Word (`.docx`).")
        st.markdown("- **Soporte Multilingüe:** Contenido comercial en varios idiomas.")

    with col2:
        st.markdown("### 💳 Mediante Pago / Suscripción")
        st.write("Suscripción Mensual: **$19 USD / mes** (~$60.000 COP)")
        st.markdown("---")
        st.markdown("#### 📱 Métodos de Pago Directos:")
        st.markdown(" - **Nequi:** `3164142727`")
        st.markdown(" - **PSE / Cuenta:** `3164142727`")
        st.markdown("---")
        st.write("Obtén tu clave de acceso inmediata enviando tu comprobante de pago por WhatsApp.")
        
        mi_numero_whatsapp = "573164142727" 
        mensaje = "Hola,%20ya%20realicé%20el%20pago.%20Quiero%20mi%20clave%20de%20licencia%20para%20InmoIA%20Pro."
        link_wa = f"https://wa.me/{mi_numero_whatsapp}?text={mensaje}"
        
        st.link_button("📲 Confirmar Pago por WhatsApp", link_wa)

    st.stop() # Detiene la ejecución si no hay clave activa

# ---------------------------------------------------------
# 3. APLICACIÓN PRINCIPAL (SOLO PARA USUARIOS PAGADOS)
# ---------------------------------------------------------
st.title("🏠 InmoIA Global: Generador Multilingüe de Propiedades")
st.caption("Crea la ficha web, copies para redes, mensajes de WhatsApp y guiones de video en segundos.")

# Configuración de Groq API en la barra lateral
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Configuración de IA")
api_key_input = st.sidebar.text_input("Clave API Groq (gsk_...):", type="password")

modelo_seleccionado = st.sidebar.selectbox(
    "Modelo de IA Activo (Groq):",
    ["llama-3.3-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"]
)

idioma = st.sidebar.selectbox(
    "Idioma del contenido:",
    ["Español es", "Inglés en", "Portugués pt", "Francés fr"]
)

# Formulario principal
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📋 Datos Generales")
    tipo_propiedad = st.selectbox("Tipo de Propiedad:", ["Apartamento", "Casa", "Lote / Terreno", "Oficina", "Local Comercial"])
    tipo_operacion = st.radio("Tipo de Operación:", ["Venta", "Arriendo / Alquiler"], horizontal=True)
    precio = st.text_input("Precio y Moneda:", placeholder="Ej: $180.000 USD o $2.500.000 COP")
    ubicacion = st.text_input("Ubicación (Ciudad / Barrio):", placeholder="Ej: El Poblado, Medellín")

with col_b:
    st.subheader("📐 Especificaciones Técnicas")
    habitaciones = st.number_input("Habitaciones / Dormitorios:", min_value=0, value=3)
    banos = st.number_input("Baños:", min_value=0, value=2)
    area = st.text_input("Área construida (m² o pies²):", placeholder="Ej: 95 m²")
    estacionamiento = st.text_input("Estacionamiento / Garajes:", placeholder="Ej: 2 parqueaderos cubiertos")

detalles_extra = st.text_area("Detalles adicionales / Amenidades:", placeholder="Ej: Piscina, vista a la ciudad, balcón amplio, seguridad 24/7...")

# Generación con IA
if st.button("🚀 Generar Todo el Contenido Comercial", type="primary"):
    if not api_key_input:
        st.error("Por favor, ingresa tu API Key de Groq en la barra lateral para continuar.")
    else:
        try:
            client = Groq(api_key=api_key_input)
            
            prompt = f"""
            Eres un experto en Copywriting Inmobiliario Internacional. Genera una propuesta comercial completa en idioma '{idioma}'.
            
            DATOS DE LA PROPIEDAD:
            - Tipo: {tipo_propiedad}
            - Operación: {tipo_operacion}
            - Precio: {precio}
            - Ubicación: {ubicacion}
            - Habitaciones: {habitaciones}
            - Baños: {banos}
            - Área: {area}
            - Parqueaderos: {estacionamiento}
            - Detalles/Amenidades: {detalles_extra}
            
            Genera las siguientes secciones claramente divididas:
            1. 📝 Ficha Web Comercial (Título atractivo y descripción detallada).
            2. 📸 Copy para Instagram / Facebook (Con emojis y hashtags inmobiliarios).
            3. 💬 Mensaje Directo para WhatsApp (Persuasivo y directo).
            4. 🎬 Guión corto para Video / Reel / TikTok (Con indicaciones visuales).
            """

            with st.spinner("Generando contenido con IA..."):
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=modelo_seleccionado,
                )
                resultado = chat_completion.choices[0].message.content
                st.session_state['resultado_ia'] = resultado

        except Exception as e:
            st.error(f"Error al conectar con Groq: {e}")

# Muestra del resultado y descarga en Word
if 'resultado_ia' in st.session_state:
    st.markdown("---")
    st.subheader("📄 Contenido Comercial Generado")
    st.write(st.session_state['resultado_ia'])

    # Creación del documento Word
    doc = Document()
    doc.add_heading(f"Propuesta Comercial - {tipo_propiedad} en {ubicacion}", 0)
    doc.add_paragraph(st.session_state['resultado_ia'])
    
    bio = BytesIO()
    doc.save(bio)
    
    st.download_button(
        label="📥 Descargar Ficha Comercial en Word (.docx)",
        data=bio.getvalue(),
        file_name=f"InmoIA_{tipo_propiedad}_{ubicacion}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
