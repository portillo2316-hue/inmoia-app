import streamlit as st
from google import genai

st.set_page_config(page_title="InmoIA Pro", page_icon="🏠", layout="wide")

st.sidebar.title("🔐 Acceso InmoIA Pro")
clave_licencia = st.sidebar.text_input("Ingresa tu Clave de Licencia:", type="password")

if clave_licencia.lower() in ["inmoia2026", "inmo2026", "admin"]:
    st.sidebar.success("¡Licencia Activa y Verificada!")
    acceso_concedido = True
else:
    if clave_licencia:
        st.sidebar.error("Clave incorrecta.")
    acceso_concedido = False

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Configuración de IA")
gemini_api_key = st.sidebar.text_input("Clave API Gemini (AIza...):", type="password")

idioma_contenido = st.sidebar.selectbox("Idioma:", ["Español", "Inglés", "Portugués"])

st.title("🏠 InmoIA Global: Generador de Propiedades")

if acceso_concedido:
    col1, col2 = st.columns(2)
    with col1:
        tipo_propiedad = st.selectbox("Tipo", ["Apartamento", "Casa", "Local", "Oficina", "Lote"])
        precio = st.text_input("Precio", "220.000 USD")
        ubicacion = st.text_input("Ubicación", "Medellín")
    with col2:
        area = st.text_input("Área", "90 m²")
        garajes = st.text_input("Parqueaderos", "2")
        hab_banos = st.text_input("Habitaciones / Baños", "3 hab, 2 baños")

    detalles = st.text_area("Amenidades", "Piscina, seguridad 24/7, vista panorámica.")

    if st.button("🚀 Generar Todo el Contenido Comercial", type="primary"):
        if not gemini_api_key:
            st.error("⚠️ Ingresa tu Clave API de Gemini en la barra lateral.")
        else:
            try:
                client = genai.Client(api_key=gemini_api_key)
                prompt = f"""
                Actúa como experto en marketing inmobiliario.
                Genera la ficha web, copy para redes con hashtags y mensaje de WhatsApp para:
                - Tipo: {tipo_propiedad}, Ubicación: {ubicacion}, Precio: {precio}
                - Área: {area}, Garajes: {garajes}, Distribución: {hab_banos}
                - Amenidades: {detalles}
                - Idioma: {idioma_contenido}
                """
                
                with st.spinner("Generando contenido con Gemini..."):
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                    )
                
                st.success("¡Contenido generado con éxito!")
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Error al conectar con la IA: {e}")
