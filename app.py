# ============================================================
# BASE DE DATOS
# ============================================================

DB_NAME = "inmoia.db"


def conectar_db():
    """
    Abre conexión con SQLite.
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
            titulo TEXT NOT NULL,
            ciudad TEXT NOT NULL,
            tipo TEXT NOT NULL,
            precio TEXT NOT NULL,
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
    Comprueba si la base de datos antigua tiene todas las columnas
    necesarias.

    Si falta alguna columna, la agrega automáticamente.

    Esto permite actualizar InmoIA sin perder las propiedades
    que ya estaban guardadas.
    """

    conn = conectar_db()
    cursor = conn.cursor()

    # Obtener columnas existentes
    cursor.execute(
        "PRAGMA table_info(propiedades)"
    )

    columnas_existentes = {
        columna[1]
        for columna in cursor.fetchall()
    }

    # Columnas que nuestra versión actual necesita
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

    # Agregar columnas que no existan
    for nombre_columna, tipo_columna in columnas_necesarias.items():

        if nombre_columna not in columnas_existentes:

            cursor.execute(
                f"""
                ALTER TABLE propiedades
                ADD COLUMN {nombre_columna} {tipo_columna}
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


# ============================================================
# INICIALIZAR Y MIGRAR BASE DE DATOS
# ============================================================

crear_tablas()

migrar_base_datos()
