import streamlit as st
from google import genai
import sqlite3
import time

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="InmoIA Pro - Global Real Estate AI",
    page_icon="🏠",
    layout="wide"
)

DB_NAME = "inmoia.db"


# =========================================================
# BASE DE DATOS SQLITE
# =========================================================

def conectar_db():
    return sqlite3.connect(DB_NAME)


def crear_tablas():
    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS propiedades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            precio TEXT,
            ubicacion TEXT,
            area TEXT,
            garajes TEXT,
            habitaciones_banos TEXT,
            amenidades TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conexion.commit()
    conexion.close()


def guardar_propiedad(
    tipo,
    precio,
    ubicacion,
    area,
    garajes,
    habitaciones_banos,
    amenidades
):
    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO propiedades (
            tipo,
            precio,
            ubicacion,
            area,
            garajes,
            habitaciones_banos,
            amenidades
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        tipo,
        precio,
        ubicacion,
        area,
        garajes,
        habitaciones_banos,
        amenidades
    ))

    conexion.commit()
    conexion.close()


def obtener_propiedades():
    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            tipo,
            precio,
            ubicacion,
            area,
            garajes,
            habitaciones_banos,
            amenidades
        FROM propiedades
        ORDER BY id DESC
    """)

    propiedades = cursor.fetchall()

    conexion.close()

    return propiedades


def eliminar_propiedad(id_propiedad):
    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM propiedades WHERE id = ?",
        (id_propiedad,)
    )

    conexion.commit()
    conexion.close()


# Crear las tablas al iniciar la aplicación
crear_tablas()


# =========================================================
# GESTIÓN DE PARÁMETROS URL
# =========================================================

query_params = st.query_params
url_access = query_params.get("access", "")


# =========================================================
# BARRA LATERAL
# =========================================================

st.sidebar.title("🔐 Acceso Clientes")

clave_licencia = st.sidebar.text_input(
    "Clave de Licencia:",
    type="password",
    value=url_access
)

licencias_validas = [
    "inmoia2026",
    "inmo2026",
    "admin"
]

if clave_licencia.strip().lower() in licencias_validas:
    st.sidebar.success("¡Licencia Activa y Verificada!")
    acceso_concedido = True
else:
    acceso_concedido = False

    if clave_licencia:
        st.sidebar.error("Licencia incorrecta.")
    else:
        st.sidebar.warning(
            "Ingresa tu licencia para activar el software."
        )


st.sidebar.markdown("---")

st.sidebar.subheader("⚙️ Configuración IA Global")

gemini_api_key = st.sidebar.text_input(
    "Clave API Gemini:",
    type="password"
)

idioma_contenido = st.sidebar.selectbox(
    "🌍 Idioma del Contenido:",
    [
        "Español",
        "English (Inglés)",
        "Português (Portugués)",
        "Français (Francés)",
        "Deutsch (Alemán)",
        "Italiano"
    ]
)


# =========================================================
# ENCABEZADO
# =========================================================

st.title(
    "🏠 InmoIA Pro: El Superpoder Global para Inmobiliarias con IA"
)

st.markdown(
    "### Multiplica tus ventas creando descripciones persuasivas, "
    "copies para redes y guiones de video en segundos."
)


# =========================================================
# BENEFICIOS
# =========================================================

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("✨ **Fichas Web Persuasivas**")
    st.caption(
        "Redactadas con IA para presentar mejor tus propiedades."
    )

with col_b:
    st.markdown("📱 **Redes Sociales & WhatsApp**")
    st.caption(
        "Copies listos para Instagram, Facebook y chats."
    )

with col_c:
    st.markdown("🎬 **Guiones para Reels / TikTok**")
    st.caption(
        "Guiones diseñados para captar la atención."
    )


st.markdown("---")


# =========================================================
# PLANES Y PAGOS
# =========================================================

st.subheader("💳 Planes y Suscripción InmoIA Pro")

col_pago1, col_pago2 = st.columns(2)

with col_pago1:

    st.markdown("""
    #### 🚀 Acceso Mensual

    **Precio:** `$50.000 COP` / `15 USD` al mes

    **Incluye:**

    - Generación multilingüe
    - Perfiles de clientes objetivo
    - Respuestas para WhatsApp
    - Guiones para redes
    - Herramientas de IA inmobiliaria
    """)

    st.markdown(
        """
        <a href="https://mpago.li/tutu-link-de-ejemplo"
        target="_blank">
            <div style="
                display:flex;
                align-items:center;
                justify-content:center;
                background-color:#009EE3;
                color:white;
                padding:12px 20px;
                border-radius:8px;
                text-decoration:none;
                font-weight:bold;
                font-size:16px;">
                💳 Pagar Suscripción
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )


with col_pago2:

    st.markdown("""
    #### 📱 Pago Directo por Nequi

    **Número Nequi:** `316 414 2727`

    Realiza la transferencia de `$50.000 COP`
    y envíanos el comprobante por WhatsApp.
    """)

    st.markdown(
        """
        <a href="https://wa.me/573164142727"
        target="_blank">
            <div style="
                display:flex;
                align-items:center;
                justify-content:center;
                background-color:#25D366;
                color:white;
                padding:12px 20px;
                border-radius:8px;
                text-decoration:none;
                font-weight:bold;
                font-size:16px;">
                💬 Enviar Comprobante por WhatsApp
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )


st.markdown("---")


# =========================================================
# ZONA PÚBLICA
# =========================================================

if not acceso_concedido:

    st.info(
        "💡 **El generador está bloqueado.** "
        "Ingresa una licencia válida para acceder al panel."
    )

    with st.expander("👀 Ver ejemplo del contenido generado"):

        st.markdown("""
        **Ficha Web**

        Espectacular apartamento moderno con vista panorámica...

        **WhatsApp**

        ¡Oportunidad única! Apartamento de 90m² con piscina...

        **Reel/TikTok**

        ¿Buscas el hogar de tus sueños? Mira esto...
        """)


# =========================================================
# ZONA PROTEGIDA
# =========================================================

else:

    st.success(
        "🚀 ¡Bienvenido al panel operativo de InmoIA Pro!"
    )

    # =====================================================
    # TABS PRINCIPALES
    # =====================================================

    tab_propiedades, tab_generador = st.tabs([
        "🏠 Mis Propiedades",
        "🤖 Generador IA"
    ])


    # =====================================================
    # TAB PROPIEDADES
    # =====================================================

    with tab_propiedades:

        st.header("🏠 Mis Propiedades")

        tab_nueva, tab_lista = st.tabs([
            "➕ Nueva Propiedad",
            "📋 Mis Propiedades"
        ])


        # -------------------------------------------------
        # NUEVA PROPIEDAD
        # -------------------------------------------------

        with tab_nueva:

            st.subheader("Registrar nueva propiedad")

            col1, col2 = st.columns(2)

            with col1:

                tipo_propiedad = st.selectbox(
                    "Tipo de Inmueble",
                    [
                        "Apartamento",
                        "Casa",
                        "Local Comercial",
                        "Oficina",
                        "Lote"
                    ]
                )

                precio = st.text_input(
                    "Precio y Moneda",
                    "220.000 USD"
                )

                ubicacion = st.text_input(
                    "Ubicación",
                    "Medellín, Colombia"
                )

                area = st.text_input(
                    "Área construida",
                    "90 m²"
                )


            with col2:

                garajes = st.text_input(
                    "Estacionamiento / Garajes",
                    "2 parqueaderos"
                )

                habitaciones_banos = st.text_input(
                    "Habitaciones y Baños",
                    "3 habitaciones, 2 baños"
                )

                amenidades = st.text_area(
                    "Amenidades",
                    "Piscina, seguridad 24/7, "
                    "vista panorámica, excelente iluminación natural."
                )


            if st.button(
                "💾 Guardar Propiedad",
                type="primary"
            ):

                if not ubicacion.strip():

                    st.error(
                        "La ubicación es obligatoria."
                    )

                else:

                    guardar_propiedad(
                        tipo_propiedad,
                        precio,
                        ubicacion,
                        area,
                        garajes,
                        habitaciones_banos,
                        amenidades
                    )

                    st.success(
                        "✅ Propiedad guardada correctamente."
                    )


        # -------------------------------------------------
        # LISTA DE PROPIEDADES
        # -------------------------------------------------

        with tab_lista:

            st.subheader("📋 Propiedades registradas")

            propiedades = obtener_propiedades()

            if not propiedades:

                st.info(
                    "Todavía no tienes propiedades registradas."
                )

            else:

                for propiedad in propiedades:

                    (
                        id_propiedad,
                        tipo,
                        precio,
                        ubicacion,
                        area,
                        garajes,
                        habitaciones_banos,
                        amenidades
                    ) = propiedad


                    with st.expander(
                        f"🏠 {tipo} | {ubicacion} | {precio}"
                    ):

                        col_info, col_accion = st.columns(
                            [4, 1]
                        )

                        with col_info:

                            st.write(
                                f"**ID:** {id_propiedad}"
                            )

                            st.write(
                                f"**Tipo:** {tipo}"
                            )

                            st.write(
                                f"**Precio:** {precio}"
                            )

                            st.write(
                                f"**Ubicación:** {ubicacion}"
                            )

                            st.write(
                                f"**Área:** {area}"
                            )

                            st.write(
                                f"**Garajes:** {garajes}"
                            )

                            st.write(
                                f"**Distribución:** "
                                f"{habitaciones_banos}"
                            )

                            st.write(
                                f"**Amenidades:** {amenidades}"
                            )


                        with col_accion:

                            if st.button(
                                "🗑️ Eliminar",
                                key=f"eliminar_{id_propiedad}"
                            ):

                                eliminar_propiedad(
                                    id_propiedad
                                )

                                st.success(
                                    "Propiedad eliminada."
                                )

                                st.rerun()


    # =====================================================
    # TAB GENERADOR IA
    # =====================================================

    with tab_generador:

        st.header("🤖 Generador de Contenido IA")

        propiedades = obtener_propiedades()

        if not propiedades:

            st.warning(
                "Primero debes registrar al menos "
                "una propiedad."
            )

        else:

            opciones_propiedades = {}

            for propiedad in propiedades:

                (
                    id_propiedad,
                    tipo,
                    precio,
                    ubicacion,
                    area,
                    garajes,
                    habitaciones_banos,
                    amenidades
                ) = propiedad

                etiqueta = (
                    f"#{id_propiedad} - "
                    f"{tipo} - "
                    f"{ubicacion} - "
                    f"{precio}"
                )

                opciones_propiedades[etiqueta] = propiedad


            propiedad_seleccionada = st.selectbox(
                "🏠 Selecciona la propiedad",
                list(opciones_propiedades.keys())
            )


            propiedad = opciones_propiedades[
                propiedad_seleccionada
            ]


            (
                id_propiedad,
                tipo_propiedad,
                precio_moneda,
                ubicacion,
                area,
                garajes,
                habitaciones_banos,
                detalles_adicionales
            ) = propiedad


            st.markdown("### Datos de la propiedad")

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"**Tipo:** {tipo_propiedad}"
                )

                st.write(
                    f"**Precio:** {precio_moneda}"
                )

                st.write(
                    f"**Ubicación:** {ubicacion}"
                )

                st.write(
                    f"**Área:** {area}"
                )


            with col2:

                st.write(
                    f"**Garajes:** {garajes}"
                )

                st.write(
                    f"**Distribución:** "
                    f"{habitaciones_banos}"
                )

                st.write(
                    f"**Amenidades:** "
                    f"{detalles_adicionales}"
                )


            perfil_cliente = st.selectbox(
                "🎯 Perfil del Cliente Objetivo",
                [
                    "Familias",
                    "Inversionistas Globales",
                    "Jóvenes profesionales",
                    "Expatriados / Turistas"
                ]
            )


            tono_comercial = st.selectbox(
                "🗣️ Tono del Copy",
                [
                    "Persuasivo y Emocional",
                    "Corporativo y Elegante",
                    "Urgente / Alta Conversión"
                ]
            )


            if st.button(
                "🚀 Generar Contenido Comercial Global",
                type="primary"
            ):

                if not gemini_api_key:

                    st.error(
                        "⚠️ Por favor ingresa tu "
                        "Clave API de Gemini en la barra lateral."
                    )

                else:

                    prompt = f"""
                    Actúa como un experto copywriter
                    inmobiliario internacional y especialista
                    en marketing digital global.

                    Genera contenido comercial persuasivo
                    y profesional adaptado estrictamente
                    al idioma de salida:
                    {idioma_contenido}.

                    DATOS DEL INMUEBLE:

                    Tipo:
                    {tipo_propiedad}

                    Ubicación:
                    {ubicacion}

                    Precio:
                    {precio_moneda}

                    Área:
                    {area}

                    Distribución:
                    {habitaciones_banos}

                    Estacionamiento:
                    {garajes}

                    Amenidades:
                    {detalles_adicionales}

                    Perfil del comprador:
                    {perfil_cliente}

                    Tono comercial:
                    {tono_comercial}


                    ESTRUCTURA DE LA RESPUESTA:

                    1. 🏡 Ficha Técnica &
                       Descripción Web Persuasiva

                    2. 📱 Copy para Redes Sociales
                       con hashtags relevantes

                    3. 💬 Mensaje Vendedor
                       para WhatsApp

                    4. 🤖 Respuestas Rápidas
                       Conversacionales para Chat

                    5. 🎬 Guion para Reel / TikTok
                       de aproximadamente 30 segundos

                    No inventes características que
                    no estén presentes en los datos
                    proporcionados.
                    """


                    # Modelos de respaldo
                    modelos_a_probar = [
                        "gemini-3.8-flash",
                        "gemini-3.6-flash"
                    ]


                    exito = False
                    resultado_ia = ""
                    error_msg = ""


                    try:

                        client = genai.Client(
                            api_key=gemini_api_key.strip()
                        )

                    except Exception as e:

                        st.error(
                            f"Error configurando Gemini: {e}"
                        )

                        client = None


                    if client:

                        with st.spinner(
                            f"Generando contenido en "
                            f"{idioma_contenido}..."
                        ):

                            for modelo in modelos_a_probar:

                                for intento in range(2):

                                    try:

                                        response = (
                                            client.models
                                            .generate_content(
                                                model=modelo,
                                                contents=prompt
                                            )
                                        )

                                        resultado_ia = (
                                            response.text
                                        )

                                        exito = True

                                        break


                                    except Exception as e:

                                        error_msg = str(e)

                                        if (
                                            "503" in str(e)
                                            and intento == 0
                                        ):

                                            time.sleep(1.5)
                                            continue

                                        break


                                if exito:
                                    break


                        if exito:

                            st.success(
                                "✅ Contenido generado "
                                "correctamente."
                            )

                            st.markdown("---")

                            st.markdown(
                                resultado_ia
                            )

                        else:

                            st.error(
                                f"Error al conectar "
                                f"con la IA: {error_msg}"
                            )

                            st.info(
                                "Revisa tu API Key de Gemini "
                                "y vuelve a intentarlo."
                            )
