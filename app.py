import streamlit as st
from google import genai
import sqlite3
import time
from datetime import datetime


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="InmoIA Pro - Global Real Estate AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)


DB_NAME = "inmoia.db"


# ============================================================
# MODELOS GEMINI
# ============================================================
#
# No dependemos de un solo modelo.
#
# Si un modelo devuelve 503 / 429 / 404, el sistema intenta
# automáticamente con el siguiente.
#
# Google actualmente mantiene estos modelos disponibles:
# - gemini-3.5-flash
# - gemini-3.6-flash
# - gemini-3.5-flash-lite
# - gemini-3.1-flash-lite
# - gemini-2.5-flash
#
# Para InmoIA utilizamos primero modelos Flash y luego Lite
# como respaldo.
# ============================================================

MODELOS_GEMINI = [
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
]


# ============================================================
# BASE DE DATOS
# ============================================================

def conectar_db():
    """
    Abre conexión con SQLite.
    """
    return sqlite3.connect(DB_NAME)


def crear_tablas():
    """
    Crea la tabla de propiedades si todavía no existe.
    """

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS propiedades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            ciudad TEXT NOT NULL,
            tipo TEXT NOT NULL,
            precio TEXT NOT NULL,
            habitaciones INTEGER DEFAULT 0,
            banos INTEGER DEFAULT 0,
            area REAL DEFAULT 0,
            descripcion TEXT,
            fecha_creacion TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def guardar_propiedad(
    titulo,
    ciudad,
    tipo,
    precio,
    habitaciones,
    banos,
    area,
    descripcion,
):
    """
    Guarda una propiedad en SQLite.
    """

    conn = conectar_db()
    cursor = conn.cursor()

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO propiedades (
            titulo,
            ciudad,
            tipo,
            precio,
            habitaciones,
            banos,
            area,
            descripcion,
            fecha_creacion
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            titulo,
            ciudad,
            tipo,
            precio,
            habitaciones,
            banos,
            area,
            descripcion,
            fecha,
        ),
    )

    conn.commit()
    conn.close()


def obtener_propiedades():
    """
    Obtiene todas las propiedades guardadas.
    """

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            titulo,
            ciudad,
            tipo,
            precio,
            habitaciones,
            banos,
            area,
            descripcion,
            fecha_creacion
        FROM propiedades
        ORDER BY id DESC
        """
    )

    propiedades = cursor.fetchall()

    conn.close()

    return propiedades


def obtener_propiedad_por_id(propiedad_id):
    """
    Obtiene una propiedad específica.
    """

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            titulo,
            ciudad,
            tipo,
            precio,
            habitaciones,
            banos,
            area,
            descripcion,
            fecha_creacion
        FROM propiedades
        WHERE id = ?
        """,
        (propiedad_id,),
    )

    propiedad = cursor.fetchone()

    conn.close()

    return propiedad


def eliminar_propiedad(propiedad_id):
    """
    Elimina una propiedad.
    """

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM propiedades
        WHERE id = ?
        """,
        (propiedad_id,),
    )

    conn.commit()
    conn.close()


# Crear base de datos y tabla
crear_tablas()


# ============================================================
# FUNCIONES GEMINI
# ============================================================

def detectar_tipo_error(error):
    """
    Intenta identificar el tipo de error devuelto por Gemini.
    """

    mensaje = str(error).lower()

    if "429" in mensaje:
        return "429"

    if "503" in mensaje:
        return "503"

    if "500" in mensaje:
        return "500"

    if "404" in mensaje:
        return "404"

    if "401" in mensaje:
        return "401"

    if "403" in mensaje:
        return "403"

    if "400" in mensaje:
        return "400"

    return "otro"


def error_es_reintentable(error):
    """
    Determina si conviene volver a intentar o pasar al siguiente modelo.
    """

    tipo = detectar_tipo_error(error)

    return tipo in ["429", "500", "503", "404"]


def generar_con_ia(api_key, prompt):
    """
    Función central de IA de InmoIA Pro.

    Esta función:
    1. Recibe la API Key.
    2. Prueba el primer modelo.
    3. Si falla temporalmente, reintenta.
    4. Si continúa fallando, cambia de modelo.
    5. Devuelve el texto generado.

    Así el resto de la aplicación NO necesita saber qué modelo
    de Gemini está utilizando.
    """

    if not api_key:
        return {
            "ok": False,
            "texto": "",
            "modelo": "",
            "error": "No se proporcionó una API Key de Gemini.",
        }

    try:
        client = genai.Client(api_key=api_key)
    except Exception as error:
        return {
            "ok": False,
            "texto": "",
            "modelo": "",
            "error": f"No fue posible conectar con Gemini: {error}",
        }

    errores = []

    # Recorremos todos los modelos
    for modelo in MODELOS_GEMINI:

        # Máximo 2 intentos por modelo
        for intento in range(2):

            try:

                respuesta = client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                )

                texto = getattr(respuesta, "text", None)

                if texto and texto.strip():

                    return {
                        "ok": True,
                        "texto": texto.strip(),
                        "modelo": modelo,
                        "error": "",
                    }

                errores.append(
                    f"{modelo}: respuesta vacía"
                )

                break

            except Exception as error:

                tipo_error = detectar_tipo_error(error)

                errores.append(
                    f"{modelo}: error {tipo_error}"
                )

                # Errores de autenticación/configuración.
                # No tiene sentido probar 5 modelos si la API Key
                # está incorrecta.
                if tipo_error in ["400", "401", "403"]:

                    return {
                        "ok": False,
                        "texto": "",
                        "modelo": modelo,
                        "error": (
                            "Gemini rechazó la solicitud. "
                            "Verifica que tu API Key sea correcta "
                            "y tenga acceso a la Gemini API.\n\n"
                            f"Detalle: {error}"
                        ),
                    }

                # Si es un error temporal, hacemos retry.
                if error_es_reintentable(error):

                    if intento == 0:
                        time.sleep(2)
                        continue

                    # Después del segundo intento,
                    # pasamos al siguiente modelo.
                    break

                # Error desconocido.
                break

    return {
        "ok": False,
        "texto": "",
        "modelo": "",
        "error": (
            "En este momento no fue posible generar el contenido "
            "con los modelos disponibles.\n\n"
            "El sistema probó automáticamente varios modelos de Gemini.\n\n"
            f"Diagnóstico técnico: {', '.join(errores)}"
        ),
    }


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🏠 InmoIA Pro")

    st.caption("Global Real Estate AI")

    st.divider()

    st.subheader("🔐 Acceso")

    licencia = st.text_input(
        "Licencia",
        type="password",
        placeholder="Introduce tu licencia",
    )

    # Licencias actuales de desarrollo
    LICENCIAS_VALIDAS = [
        "inmoia2026",
        "inmo2026",
        "admin",
    ]

    acceso = licencia in LICENCIAS_VALIDAS

    if acceso:
        st.success("Licencia válida")

    else:
        st.info(
            "Introduce una licencia válida para acceder "
            "al panel."
        )

    st.divider()

    st.subheader("🤖 Configuración IA")

    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Durante el desarrollo puedes introducir aquí tu API Key.",
    )

    if api_key:
        st.success("API Key recibida")

    st.divider()

    idioma = st.selectbox(
        "🌎 Idioma",
        [
            "Español",
            "English",
        ],
    )

    st.divider()

    st.caption(
        "InmoIA Pro © 2026"
    )


# ============================================================
# ENCABEZADO
# ============================================================

st.title("🏠 InmoIA Pro")

st.subheader(
    "La inteligencia artificial para agentes inmobiliarios"
)

st.write(
    """
    Crea descripciones de propiedades, publicaciones para redes,
    mensajes comerciales y guiones para videos utilizando IA.
    """
)


# ============================================================
# PÁGINA DE INICIO SI NO HAY ACCESO
# ============================================================

if not acceso:

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            ### 🏡 Propiedades

            Guarda y organiza tus propiedades
            inmobiliarias.
            """
        )

    with col2:
        st.markdown(
            """
            ### 🤖 Inteligencia Artificial

            Genera contenido comercial
            automáticamente.
            """
        )

    with col3:
        st.markdown(
            """
            ### 📱 Redes y WhatsApp

            Crea textos listos para publicar
            y enviar a clientes.
            """
        )

    st.divider()

    st.subheader("💰 Plan InmoIA Pro")

    precio_col1, precio_col2 = st.columns(2)

    with precio_col1:

        st.markdown(
            """
            ## $50.000 COP

            **por mes**

            Incluye:

            - Gestión de propiedades
            - Generación de contenido con IA
            - Textos para redes sociales
            - Mensajes para WhatsApp
            - Guiones para Reels/TikTok
            """
        )

    with precio_col2:

        st.markdown("### 💳 Métodos de pago")

        st.write(
            "Mercado Pago"
        )

        st.code(
            "https://mpago.li/tutu-link-de-ejemplo"
        )

        st.write(
            "Nequi"
        )

        st.code(
            "316 414 2727"
        )

        st.markdown(
            """
            ### 📲 WhatsApp

            [Escribir por WhatsApp](https://wa.me/573164142727)
            """
        )

    st.info(
        "Introduce tu licencia en el menú lateral "
        "para entrar al sistema."
    )

    st.stop()


# ============================================================
# PANEL PRINCIPAL
# ============================================================

st.success("Bienvenido a InmoIA Pro 🚀")

tab_propiedades, tab_ia = st.tabs(
    [
        "🏠 Mis Propiedades",
        "🤖 Generador IA",
    ]
)


# ============================================================
# TAB 1 - PROPIEDADES
# ============================================================

with tab_propiedades:

    st.header("🏠 Mis Propiedades")

    st.write(
        "Guarda las propiedades que posteriormente "
        "utilizarás para generar contenido."
    )

    st.divider()

    st.subheader("➕ Registrar nueva propiedad")

    col1, col2 = st.columns(2)

    with col1:

        titulo = st.text_input(
            "Título de la propiedad",
            placeholder="Apartamento moderno en el norte",
        )

        ciudad = st.text_input(
            "Ciudad",
            placeholder="Cali",
        )

        tipo = st.selectbox(
            "Tipo de propiedad",
            [
                "Apartamento",
                "Casa",
                "Oficina",
                "Local comercial",
                "Lote",
                "Finca",
                "Bodega",
                "Penthouse",
                "Otro",
            ],
        )

        precio = st.text_input(
            "Precio",
            placeholder="$350.000.000",
        )

    with col2:

        habitaciones = st.number_input(
            "Habitaciones",
            min_value=0,
            max_value=100,
            value=3,
            step=1,
        )

        banos = st.number_input(
            "Baños",
            min_value=0,
            max_value=100,
            value=2,
            step=1,
        )

        area = st.number_input(
            "Área en m²",
            min_value=0.0,
            max_value=100000.0,
            value=80.0,
            step=1.0,
        )

    descripcion = st.text_area(
        "Descripción de la propiedad",
        placeholder=(
            "Describe las características principales, "
            "ubicación, acabados, zonas sociales, parqueadero, "
            "vista, seguridad, etc."
        ),
        height=150,
    )

    st.divider()

    if st.button(
        "💾 Guardar propiedad",
        type="primary",
        use_container_width=True,
    ):

        if not titulo.strip():
            st.error(
                "Debes introducir el título de la propiedad."
            )

        elif not ciudad.strip():
            st.error(
                "Debes introducir la ciudad."
            )

        elif not precio.strip():
            st.error(
                "Debes introducir el precio."
            )

        else:

            try:

                guardar_propiedad(
                    titulo=titulo.strip(),
                    ciudad=ciudad.strip(),
                    tipo=tipo,
                    precio=precio.strip(),
                    habitaciones=int(habitaciones),
                    banos=int(banos),
                    area=float(area),
                    descripcion=descripcion.strip(),
                )

                st.success(
                    "✅ Propiedad guardada correctamente."
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"No fue posible guardar la propiedad: {error}"
                )

    st.divider()

    st.subheader("📋 Propiedades guardadas")

    propiedades = obtener_propiedades()

    if not propiedades:

        st.info(
            "Todavía no tienes propiedades guardadas."
        )

    else:

        for propiedad in propiedades:

            (
                propiedad_id,
                titulo_db,
                ciudad_db,
                tipo_db,
                precio_db,
                habitaciones_db,
                banos_db,
                area_db,
                descripcion_db,
                fecha_db,
            ) = propiedad

            with st.expander(
                f"🏠 {titulo_db} — {ciudad_db}"
            ):

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.write("**Tipo**")
                    st.write(tipo_db)

                with col2:
                    st.write("**Precio**")
                    st.write(precio_db)

                with col3:
                    st.write("**Habitaciones**")
                    st.write(habitaciones_db)

                with col4:
                    st.write("**Área**")
                    st.write(f"{area_db} m²")

                st.write(
                    f"**Baños:** {banos_db}"
                )

                if descripcion_db:
                    st.write(
                        "**Descripción:**"
                    )
                    st.write(
                        descripcion_db
                    )

                st.caption(
                    f"Registrada: {fecha_db}"
                )

                confirmar = st.checkbox(
                    "Confirmar eliminación",
                    key=f"confirmar_{propiedad_id}",
                )

                if st.button(
                    "🗑️ Eliminar propiedad",
                    key=f"eliminar_{propiedad_id}",
                ):

                    if confirmar:

                        eliminar_propiedad(
                            propiedad_id
                        )

                        st.success(
                            "Propiedad eliminada."
                        )

                        st.rerun()

                    else:

                        st.warning(
                            "Marca 'Confirmar eliminación' "
                            "antes de eliminar."
                        )


# ============================================================
# TAB 2 - GENERADOR IA
# ============================================================

with tab_ia:

    st.header("🤖 Generador de contenido con IA")

    st.write(
        """
        Selecciona una propiedad y el tipo de contenido
        que deseas generar.
        """
    )

    st.divider()

    propiedades = obtener_propiedades()

    if not propiedades:

        st.warning(
            "Primero debes registrar al menos una propiedad "
            "en la sección 'Mis Propiedades'."
        )

    else:

        # ----------------------------------------------------
        # SELECTOR DE PROPIEDAD
        # ----------------------------------------------------

        opciones_propiedades = {}

        for propiedad in propiedades:

            (
                propiedad_id,
                titulo_db,
                ciudad_db,
                tipo_db,
                precio_db,
                habitaciones_db,
                banos_db,
                area_db,
                descripcion_db,
                fecha_db,
            ) = propiedad

            etiqueta = (
                f"{titulo_db} | "
                f"{ciudad_db} | "
                f"{precio_db}"
            )

            opciones_propiedades[etiqueta] = propiedad_id

        propiedad_seleccionada = st.selectbox(
            "🏠 Selecciona una propiedad",
            list(opciones_propiedades.keys()),
        )

        propiedad_id = opciones_propiedades[
            propiedad_seleccionada
        ]

        propiedad = obtener_propiedad_por_id(
            propiedad_id
        )

        if propiedad:

            (
                propiedad_id,
                titulo_db,
                ciudad_db,
                tipo_db,
                precio_db,
                habitaciones_db,
                banos_db,
                area_db,
                descripcion_db,
                fecha_db,
            ) = propiedad

            # ------------------------------------------------
            # MOSTRAR INFORMACIÓN
            # ------------------------------------------------

            st.subheader(
                "📋 Información de la propiedad"
            )

            info1, info2, info3 = st.columns(3)

            with info1:

                st.write(
                    f"**Título:** {titulo_db}"
                )

                st.write(
                    f"**Ciudad:** {ciudad_db}"
                )

                st.write(
                    f"**Tipo:** {tipo_db}"
                )

            with info2:

                st.write(
                    f"**Precio:** {precio_db}"
                )

                st.write(
                    f"**Habitaciones:** {habitaciones_db}"
                )

                st.write(
                    f"**Baños:** {banos_db}"
                )

            with info3:

                st.write(
                    f"**Área:** {area_db} m²"
                )

                st.write(
                    f"**ID:** {propiedad_id}"
                )

            if descripcion_db:

                st.write(
                    "**Descripción:**"
                )

                st.info(
                    descripcion_db
                )

            st.divider()

            # ------------------------------------------------
            # TIPO DE CONTENIDO
            # ------------------------------------------------

            tipo_contenido = st.selectbox(
                "🎯 ¿Qué quieres generar?",
                [
                    "Descripción profesional para portal inmobiliario",
                    "Publicación para Instagram/Facebook",
                    "Mensaje comercial para WhatsApp",
                    "Respuesta rápida para un cliente",
                    "Guion para Reel/TikTok de 30 segundos",
                ],
            )

            # ------------------------------------------------
            # DATOS EXTRA
            # ------------------------------------------------

            instrucciones_extra = st.text_area(
                "✏️ Instrucciones adicionales (opcional)",
                placeholder=(
                    "Ejemplo: utiliza un tono elegante, "
                    "destaca la ubicación y termina con "
                    "un llamado a la acción."
                ),
                height=100,
            )

            # ------------------------------------------------
            # BOTÓN GENERAR
            # ------------------------------------------------

            st.divider()

            if st.button(
                "✨ Generar contenido",
                type="primary",
                use_container_width=True,
            ):

                if not api_key:

                    st.error(
                        "⚠️ Debes introducir tu Gemini API Key "
                        "en el menú lateral."
                    )

                else:

                    # ------------------------------------------------
                    # PROMPT PROFESIONAL
                    # ------------------------------------------------

                    prompt = f"""
Eres un experto en marketing inmobiliario
especializado en propiedades de Colombia.

Tu trabajo es ayudar a un agente inmobiliario
a vender y promocionar propiedades.

DATOS DE LA PROPIEDAD:

Título:
{titulo_db}

Ciudad:
{ciudad_db}

Tipo:
{tipo_db}

Precio:
{precio_db}

Habitaciones:
{habitaciones_db}

Baños:
{banos_db}

Área:
{area_db} m²

Descripción original:
{descripcion_db}

TIPO DE CONTENIDO SOLICITADO:

{tipo_contenido}

INSTRUCCIONES ADICIONALES:

{instrucciones_extra}

REGLAS:

1. Escribe en español colombiano.
2. No inventes características que no aparecen
   en los datos suministrados.
3. No inventes precios.
4. No inventes ubicaciones.
5. No inventes servicios.
6. Utiliza lenguaje comercial profesional.
7. El texto debe ser claro y atractivo.
8. Evita exageraciones falsas.
9. Si corresponde, incluye un llamado a la acción.
10. Entrega directamente el contenido final.
11. No expliques que eres una inteligencia artificial.
12. No incluyas comentarios técnicos sobre el modelo.

Genera ahora el contenido solicitado.
"""

                    # ------------------------------------------------
                    # SPINNER
                    # ------------------------------------------------

                    with st.spinner(
                        "🤖 Generando contenido..."
                    ):

                        resultado = generar_con_ia(
                            api_key=api_key,
                            prompt=prompt,
                        )

                    # ------------------------------------------------
                    # RESULTADO
                    # ------------------------------------------------

                    if resultado["ok"]:

                        st.success(
                            "✅ Contenido generado correctamente."
                        )

                        st.text_area(
                            "📝 Resultado",
                            value=resultado["texto"],
                            height=400,
                        )

                        # Modelo utilizado.
                        # Lo mostramos discretamente porque estamos
                        # todavía en fase de desarrollo.
                        st.caption(
                            f"Motor IA utilizado: {resultado['modelo']}"
                        )

                        # ------------------------------------------------
                        # COPIAR / REGENERAR
                        # ------------------------------------------------

                        st.divider()

                        st.info(
                            "Puedes copiar el contenido anterior "
                            "y utilizarlo directamente en tus canales "
                            "de venta."
                        )

                    else:

                        st.error(
                            "❌ No fue posible generar el contenido."
                        )

                        st.warning(
                            resultado["error"]
                        )


# ============================================================
# PIE DE PÁGINA
# ============================================================

st.divider()

st.caption(
    "InmoIA Pro — Global Real Estate AI"
)

st.caption(
    "Versión de desarrollo 2026"
)
