import streamlit as st
import docx
from docx import Document
from io import BytesIO
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import mercadopago

# 1. Configuración de la página
st.set_page_config(
    page_title="InmoIA Pro - SaaS Inmobiliario",
    page_icon="🏠",
    layout="wide"
)

# Token de Mercado Pago integrado directamente
MP_ACCESS_TOKEN = "APP_USR-3478647531592821-092013-2f74c843de03ec24c7fb33365ca25dc9-1703907773"

# ---------------------------------------------------------
# 2. CONTROL DE ACCESO / MURO DE PAGO CON MERCADO PAGO
# ---------------------------------------------------------
st.sidebar.title("🔐 Acceso InmoIA Pro")

# Revisar si el usuario viene de pagar exitosamente desde Mercado Pago
query_params = st.query_params
payment_status = query_params.get("collection_status", None)

if payment_status == "approved":
    # El pago fue aprobado. Generamos una clave automática temporal para este usuario
    sufijo_aleatorio = datetime.now().strftime("%d%H%M")
    nueva_clave = f"PRO-{sufijo_aleatorio}"
    
    # Registramos la clave automáticamente en Google Sheets con vigencia a 30 días
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0)
        
        nuevo_registro = pd.DataFrame([{
            "clave": nueva_clave,
            "vencimiento": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        }])
        
        df_updated = pd.concat([df, nuevo_registro], ignore_index=True)
        conn.update(data=df_updated)
        
        st.success(f"🎉 ¡Pago Exitoso! Tu nueva clave de licencia es: **{nueva_clave}** (Cópiala y guárdala).")
    except Exception as e:
        st.warning(f"Pago aprobado pero hubo un error registrando la licencia automática. Tu clave temporal es: `INMO2026`. Error: {e}")

clave = st.sidebar.text_input("Ingresa tu Clave de Licencia:", type="password")

def validar_licencia(codigo_ingresado):
    if not codigo_ingresado:
        return False, "Ingresa una clave."
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0)
        
        match = df[df['clave'].astype(str).str.strip() == codigo_ingresado.strip()]
        
        if match.empty:
            return False, "❌ Clave de licencia inválida o no registrada."
        
        fecha_vencimiento_str = str(match.iloc[0]['vencimiento'])
        fecha_vencimiento = datetime.strptime(fecha_vencimiento_str.split()[0], "%Y-%m-%d").date()
        
        hoy = datetime.now().date()
        if hoy > fecha_vencimiento:
            return False, f"⚠️ Tu licencia venció el {fecha_vencimiento}. Por favor renueva tu suscripción."
            
        return True, "✅ Licencia activa."
    except Exception as e:
        if codigo_ingresado == "INMO2026":
            return True, "✅ Licencia temporal activa."
        return False, f"Error validando licencia: {e}"

acceso_concedido = False
mensaje_estado = ""

if clave:
    acceso_concedido, mensaje_estado = validar_licencia(clave)

if not acceso_concedido:
    if clave:
        st.sidebar.error(mensaje_estado)
        
    st.title("🔒 InmoIA Pro - Plataforma Restringida")
    st.info("👋 Bienvenida/o a InmoIA. Para acceder al generador de contenido inmobiliario con IA, adquiere tu suscripción automática.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚀 ¿Qué obtienes con tu suscripción?")
        st.markdown("- **Fichas Web:** Descripciones comerciales profesionales.")
        st.markdown("- **Redes Sociales:** Copies de alta conversión para Instagram, Facebook y TikTok.")
        st.markdown("- **Ventas:** Mensajes persuasivos para WhatsApp.")
        st.markdown("- **Documentos:** Exportación directa a Word (`.docx`).")

    with col2:
        st.markdown("### 💳 Pago Automático y Seguro")
        st.write("Suscripción Mensual: **$60.000 COP (~$19 USD)**")
        st.markdown("Paga de forma inmediata con **Nequi, PSE o Tarjeta** y obtén tu clave al instante.")
        
        # Botón dinámico de Mercado Pago
        if st.button("🚀 Pagar con Mercado Pago (Nequi / PSE / Tarjeta)", type="primary"):
            try:
                sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
                
                # Obtener la URL actual de tu aplicación en Streamlit Cloud
                base_url = "https://inmoia-app.streamlit.app" # Reemplaza con tu URL exacta si cambia
                
                preference_data = {
                    "items": [
                        {
                            "title": "Suscripción Mensual InmoIA Pro",
                            "quantity": 1,
                            "unit_price": 60000.00,
                            "currency_id": "COP"
                        }
                    ],
                    "back_urls": {
                        "success": base_url,
                        "failure": base_url,
                        "pending": base_url
                    },
                    "auto_return": "approved",
                }
                
                preference_response = sdk.preference().create(preference_data)
                preference = preference_response["response"]
                init_point = preference["init_point"]
                
                # Redirigir al usuario al checkout de Mercado Pago
                st.markdown(f'<meta http-equiv="refresh" content="0;url={init_point}">', unsafe_allow_html=True)
                st.success("Redirigiendo a la pasarela segura de pago...")
            except Exception as e:
                st.error(f"Error generando el enlace de pago: {e}")

    st.stop()

# ---------------------------------------------------------
# 3. APLICACIÓN PRINCIPAL (USUARIO CON LICENCIA ACTIVA)
# ---------------------------------------------------------
st.sidebar.success("🎉 ¡Licencia Activa y Verificada!")
st.title("🏠 InmoIA Global: Generador Multilingüe de Propiedades")
st.caption("Crea la ficha web, copies para redes, mensajes de WhatsApp y guiones de video en segundos.")

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

if 'resultado_ia' in st.session_state:
    st.markdown("---")
    st.subheader("📄 Contenido Comercial Generado")
    st.write(st.session_state['resultado_ia'])

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
