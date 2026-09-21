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


# ============================================================
# CONFIGURACIÓN BASE DE DATOS
# ============================================================

DB_NAME = "inmoia.db"


# ============================================================
# MODELOS GEMINI
# ============================================================

# Se utiliza un sistema de respaldo.
#
# Si un modelo presenta un error temporal como 503 o 429,
# InmoIA intenta nuevamente y después pasa automáticamente
# al siguiente modelo.
#
# Estos IDs están actualmente documentados por Google.
MODELOS_GEMINI = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
]


# ============================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================

def conectar_db():
    """
    Conecta con la base de datos SQLite.
    """

    return sqlite3.connect(DB_NAME)


def crear_tablas():
    """
    Crea la tabla de propiedades si no existe.
    """

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS propiedades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            ciudad TEXT,
            tipo TEXT,
            precio TEXT,
            habitaciones INTEGER DEFAULT 0,
            banos INTEGER DEFAULT 0,
            area REAL DEFAULT 0,
            descripcion TEXT DEFAULT '',
            fecha_creacion TEXT DEFAULT ''
        )
        """
    )

    conn.commit()
    conn.close()


def migrar_base_datos():
    """
    Comprueba la estructura actual de SQLite.

    Si la aplicación ya tenía una base de datos antigua,
    agrega automáticamente las columnas que falten.

    No elimina las propiedades existentes.
    """

    conn = conectar_db()
    cursor = conn.cursor()

    # Comprobar que la tabla existe
    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='propiedades'
        """
    )

    tabla_existe = cursor.fetchone()

    if not tabla_existe:
        conn.close()
        return

    # Obtener columnas actuales
    cursor.execute(
        "PRAGMA table_info(propiedades)"
    )

    columnas_actuales = {
        columna[1]
        for columna in cursor.fetchall()
    }

    # Columnas necesarias
    columnas_necesarias = {
        "titulo": "TEXT",
        "ciudad": "TEXT",
        "tipo": "TEXT",
        "precio": "TEXT",
        "habitaciones": "INTEGER DEFAULT 0",
        "banos": "INTEGER DEFAULT 0",
        "area": "REAL DEFAULT 0",
        "descripcion": "TEXT DEFAULT ''",
        "fecha_creacion": "TEXT DEFAULT ''",
    }

    # Agregar columnas faltantes
    for nombre, tipo in columnas_necesarias.items():

        if nombre not in columnas_actuales:

            cursor.execute(
                f"""
                ALTER TABLE propiedades
                ADD COLUMN {nombre} {tipo}
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
    Guarda una nueva propiedad.
    """

    conn = conectar_db()
    cursor = conn.cursor()

    fecha = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

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
    Obtiene todas las propiedades.
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


# ============================================================
# INICIALIZAR BASE DE DATOS
# ============================================================

crear_tablas()
migrar_base_datos()


# ============================================================
# FUNCIONES GEMINI
# ============================================================

def obtener_codigo_error(error):
    """
    Detecta códigos comunes de error de Gemini.
    """

    mensaje = str(error).lower()

    codigos = [
        "400",
        "401",
        "403",
        "404",
        "429",
        "500",
        "502",
        "503",
        "504",
    ]

    for codigo in codigos:

        if codigo in mensaje:
            return codigo

    return "OTRO"


def es_error_temporal(error):
    """
    Determina si el error permite intentar nuevamente
    con el mismo modelo o pasar al siguiente.
    """

    codigo = obtener_codigo_error(error)

    return codigo in [
        "404",
        "429",
        "500",
        "502",
        "503",
        "504",
    ]


def generar_con_ia(api_key, prompt):
    """
    Generador central de IA de InmoIA Pro.

    Prueba varios modelos automáticamente.
    """

    if not api_key:

        return {
            "ok": False,
            "texto": "",
            "modelo": "",
            "error": "No se proporcionó la API Key.",
        }

    # Crear cliente Gemini
    try:

        client = genai.Client(
            api_key=api_key
        )

    except Exception as error:

        return {
            "ok": False,
            "texto": "",
            "modelo": "",
            "error": (
                "No fue posible conectar con Gemini.\n\n"
                f"Detalle: {error}"
            ),
        }

    errores = []

    # Probar modelos
    for modelo in MODELOS_GEMINI:

        # Dos intentos por modelo
        for intento in range(2):

            try:

                respuesta = client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                )

                texto = getattr(
                    respuesta,
                    "text",
                    None,
                )

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

                codigo = obtener_codigo_error(error)

                errores.append(
                    f"{modelo}: error {codigo}"
                )

                # API Key incorrecta o permisos
                if codigo in [
                    "400",
                    "401",
                    "403",
                ]:

                    return {
                        "ok": False,
                        "texto": "",
                        "modelo": modelo,
                        "error": (
                            "Gemini rechazó la solicitud.\n\n"
                            "Comprueba que la API Key sea correcta "
                            "y que tenga acceso a Gemini API.\n\n"
                            f"Detalle técnico: {error}"
                        ),
                    }

                # Error temporal
                if es_error_temporal(error):

                    if intento == 0:

                        # Esperar antes del segundo intento
                        time.sleep(2)

                        continue

                    # Segundo fallo:
                    # pasar al siguiente modelo
                    break

                # Error desconocido
                break

    return {
        "ok": False,
        "texto": "",
        "modelo": "",
        "error": (
            "No fue posible generar el contenido "
            "con los modelos disponibles en este momento.\n\n"
            "InmoIA probó automáticamente varios modelos "
            "de respaldo.\n\n"
            f"Diagnóstico: {', '.join(errores)}"
        ),
    }


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🏠 InmoIA Pro")

    st.caption(
        "Global Real Estate AI"
    )

    st.divider()

    # --------------------------------------------------------
    # LICENCIA
    # --------------------------------------------------------

    st.subheader("🔐 Acceso")

    licencia = st.text_input(
        "Licencia",
        type="password",
        placeholder="Introduce tu licencia",
    )

    LICENCIAS_VALIDAS = [
        "inmoia2026",
        "inmo2026",
        "admin",
    ]

    acceso = licencia in LICENCIAS_VALIDAS

    if acceso:

        st.success(
            "Licencia válida"
        )

    else:

        st.info(
            "Introduce una licencia válida."
        )

    st.divider()

    # --------------------------------------------------------
    # API KEY
    # --------------------------------------------------------

    st.subheader(
        "🤖 Configuración IA"
    )

    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="AIza...",
        help=(
            "Durante el desarrollo puedes introducir "
            "aquí tu API Key de Gemini."
        ),
    )

    if api_key:

        st.success(
            "API Key recibida"
        )

    st.divider()

    # --------------------------------------------------------
    # IDIOMA
    # --------------------------------------------------------

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
# ENCABEZADO PRINCIPAL
# ============================================================

st.title(
    "🏠 InmoIA Pro"
)

st.subheader(
    "La inteligencia artificial para agentes inmobiliarios"
)

st.write(
    """
    Crea descripciones de propiedades, publicaciones,
    mensajes comerciales y guiones para videos utilizando
    inteligencia artificial.
    """
)


# ============================================================
# USUARIO SIN ACCESO
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

    st.subheader(
        "💰 Plan InmoIA Pro"
    )

    col_precio, col_pago = st.columns(2)

    with col_precio:

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

    with col_pago:

        st.markdown(
            "### 💳 Métodos de pago"
        )

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
        "Introduce una licencia en el menú lateral "
        "para entrar al sistema."
    )

    st.stop()


# ============================================================
# USUARIO CON ACCESO
# ============================================================

st.success(
    "Bienvenido a InmoIA Pro 🚀"
)


tab_propiedades, tab_ia = st.tabs(
    [
        "🏠 Mis Propiedades",
        "🤖 Generador IA",
    ]
)


# ============================================================
# TAB PROPIEDADES
# ============================================================

with tab_propiedades:

    st.header(
        "🏠 Mis Propiedades"
    )

    st.write(
        """
        Guarda las propiedades que posteriormente
        utilizarás para generar contenido.
        """
    )

    st.divider()

    st.subheader(
        "➕ Registrar nueva propiedad"
    )

    col1, col2 = st.columns(2)

    with col1:

        titulo = st.text_input(
            "Título de la propiedad",
            placeholder=(
                "Apartamento moderno en el norte"
            ),
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
            "ubicación, acabados, zonas sociales, "
            "parqueadero, vista, seguridad, etc."
        ),
        height=150,
    )

    st.divider()

    guardar = st.button(
        "💾 Guardar propiedad",
        type="primary",
        use_container_width=True,
    )

    if guardar:

        if not titulo.strip():

            st.error(
                "Debes introducir el título."
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
                    "No fue posible guardar la propiedad."
                )

                st.code(
                    str(error)
                )

    st.divider()

    st.subheader(
        "📋 Propiedades guardadas"
    )

    try:

        propiedades = obtener_propiedades()

    except Exception as error:

        st.error(
            "No fue posible leer la base de datos."
        )

        st.code(
            str(error)
        )

        propiedades = []

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

                c1, c2, c3, c4 = st.columns(4)

                with c1:

                    st.write(
                        "**Tipo**"
                    )

                    st.write(
                        tipo_db
                    )

                with c2:

                    st.write(
                        "**Precio**"
                    )

                    st.write(
                        precio_db
                    )

                with c3:

                    st.write(
                        "**Habitaciones**"
                    )

                    st.write(
                        habitaciones_db
                    )

                with c4:

                    st.write(
                        "**Área**"
                    )

                    st.write(
                        f"{area_db} m²"
                    )

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

                if fecha_db:

                    st.caption(
                        f"Registrada: {fecha_db}"
                    )

                confirmar = st.checkbox(
                    "Confirmar eliminación",
                    key=f"confirmar_{propiedad_id}",
                )

                eliminar = st.button(
                    "🗑️ Eliminar propiedad",
                    key=f"eliminar_{propiedad_id}",
                )

                if eliminar:

                    if confirmar:

                        try:

                            eliminar_propiedad(
                                propiedad_id
                            )

                            st.success(
                                "Propiedad eliminada."
                            )

                            st.rerun()

                        except Exception as error:

                            st.error(
                                "No fue posible eliminar "
                                "la propiedad."
                            )

                            st.code(
                                str(error)
                            )

                    else:

                        st.warning(
                            "Marca primero 'Confirmar eliminación'."
                        )


# ============================================================
# TAB GENERADOR IA
# ============================================================

with tab_ia:

    st.header(
        "🤖 Generador de contenido con IA"
    )

    st.write(
        """
        Selecciona una propiedad y el contenido que
        quieres generar.
        """
    )

    st.divider()

    try:

        propiedades = obtener_propiedades()

    except Exception as error:

        st.error(
            "No fue posible acceder a las propiedades."
        )

        st.code(
            str(error)
        )

        propiedades = []

    if not propiedades:

        st.warning(
            "Primero debes registrar al menos una propiedad."
        )

    else:

        # ----------------------------------------------------
        # SELECTOR
        # ----------------------------------------------------

        opciones = {}

        for propiedad in propiedades:

            propiedad_id = propiedad[0]
            titulo_db = propiedad[1]
            ciudad_db = propiedad[2]
            precio_db = propiedad[4]

            etiqueta = (
                f"{titulo_db} | "
                f"{ciudad_db} | "
                f"{precio_db}"
            )

            opciones[etiqueta] = propiedad_id

        seleccion = st.selectbox(
            "🏠 Selecciona una propiedad",
            list(opciones.keys()),
        )

        propiedad_id = opciones[
            seleccion
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
            # INFORMACIÓN
            # ------------------------------------------------

            st.subheader(
                "📋 Información de la propiedad"
            )

            c1, c2, c3 = st.columns(3)

            with c1:

                st.write(
                    f"**Título:** {titulo_db}"
                )

                st.write(
                    f"**Ciudad:** {ciudad_db}"
                )

                st.write(
                    f"**Tipo:** {tipo_db}"
                )

            with c2:

                st.write(
                    f"**Precio:** {precio_db}"
                )

                st.write(
                    f"**Habitaciones:** {habitaciones_db}"
                )

                st.write(
                    f"**Baños:** {banos_db}"
                )

            with c3:

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

            instrucciones_extra = st.text_area(
                "✏️ Instrucciones adicionales (opcional)",
                placeholder=(
                    "Ejemplo: utiliza un tono elegante, "
                    "destaca la ubicación y termina con "
                    "un llamado a la acción."
                ),
                height=100,
            )

            st.divider()

            generar = st.button(
                "✨ Generar contenido",
                type="primary",
                use_container_width=True,
            )

            if generar:

                if not api_key:

                    st.error(
                        "⚠️ Introduce tu Gemini API Key "
                        "en el menú lateral."
                    )

                else:

                    # ----------------------------------------
                    # PROMPT
                    # ----------------------------------------

                    prompt = f"""
Eres un experto en marketing inmobiliario
especializado en propiedades de Colombia.

Ayudas a agentes inmobiliarios a crear contenido
comercial profesional.

DATOS REALES DE LA PROPIEDAD

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

Descripción:
{descripcion_db}

CONTENIDO SOLICITADO

{tipo_contenido}

INSTRUCCIONES ADICIONALES

{instrucciones_extra}

REGLAS IMPORTANTES

1. Escribe en español colombiano.
2. No inventes características.
3. No inventes precios.
4. No inventes ubicaciones.
5. No inventes amenidades.
6. No inventes información que no esté proporcionada.
7. Utiliza lenguaje comercial profesional.
8. El contenido debe ser claro y atractivo.
9. Evita afirmaciones falsas o engañosas.
10. Si corresponde, incluye un llamado a la acción.
11. Entrega directamente el contenido final.
12. No expliques el proceso interno.
13. No menciones el modelo de IA.
14. No digas que eres una inteligencia artificial.

Genera ahora el contenido solicitado.
"""

                    # ----------------------------------------
                    # GENERACIÓN
                    # ----------------------------------------

                    with st.spinner(
                        "🤖 Generando contenido..."
                    ):

                        resultado = generar_con_ia(
                            api_key=api_key,
                            prompt=prompt,
                        )

                    # ----------------------------------------
                    # RESULTADO
                    # ----------------------------------------

                    if resultado["ok"]:

                        st.success(
                            "✅ Contenido generado correctamente."
                        )

                        st.text_area(
                            "📝 Resultado",
                            value=resultado["texto"],
                            height=400,
                        )

                        st.caption(
                            "Motor utilizado: "
                            + resultado["modelo"]
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
