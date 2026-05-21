import sqlite3
import hashlib
import os
from contextlib import closing

DB = "sofalab.db"

CATALOGOS_INICIALES = ["Cuerina", "Veranera", "Nevada", "Turin", "Tornado"]


# ─── CONEXIÓN ────────────────────────────────────────────────────────────────

def conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


# ─── HASH ────────────────────────────────────────────────────────────────────

def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()


# ─── TABLAS ──────────────────────────────────────────────────────────────────

def crear_tablas() -> None:
    with closing(conectar()) as conn:
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario  TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS catalogos (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL COLLATE NOCASE
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS telas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            catalogo_id INTEGER NOT NULL,
            nombre      TEXT NOT NULL,
            imagen_blob BLOB,
            extension   TEXT,
            FOREIGN KEY (catalogo_id) REFERENCES catalogos(id) ON DELETE CASCADE
        )
        """)

        # Migración segura: agrega columnas si no existen
        for col, tipo in [("imagen_blob", "BLOB"), ("extension", "TEXT")]:
            try:
                c.execute(f"ALTER TABLE telas ADD COLUMN {col} {tipo}")
            except Exception:
                pass

        c.execute("""
        CREATE INDEX IF NOT EXISTS idx_telas_catalogo
        ON telas(catalogo_id)
        """)

        for nombre in CATALOGOS_INICIALES:
            try:
                c.execute("INSERT INTO catalogos (nombre) VALUES (?)", (nombre,))
            except sqlite3.IntegrityError:
                pass

        conn.commit()


# ─── USUARIOS ────────────────────────────────────────────────────────────────

def registrar_usuario(usuario: str, password: str) -> bool:
    try:
        with closing(conectar()) as conn:
            conn.execute(
                "INSERT INTO usuarios (usuario, password) VALUES (?, ?)",
                (usuario, _hash(password)),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def login_usuario(usuario: str, password: str) -> bool:
    with closing(conectar()) as conn:
        row = conn.execute(
            "SELECT id FROM usuarios WHERE usuario=? AND password=?",
            (usuario, _hash(password)),
        ).fetchone()
    return row is not None


def actualizar_password(usuario: str, nueva: str) -> bool:
    with closing(conectar()) as conn:
        conn.execute(
            "UPDATE usuarios SET password=? WHERE usuario=?",
            (_hash(nueva), usuario),
        )
        conn.commit()
        ok = conn.execute("SELECT changes()").fetchone()[0] > 0
    return ok


def eliminar_usuario(usuario: str) -> bool:
    with closing(conectar()) as conn:
        conn.execute("DELETE FROM usuarios WHERE usuario=?", (usuario,))
        conn.commit()
        ok = conn.execute("SELECT changes()").fetchone()[0] > 0
    return ok


# ─── CATÁLOGOS ───────────────────────────────────────────────────────────────

def crear_catalogo(nombre: str) -> bool:
    try:
        with closing(conectar()) as conn:
            conn.execute("INSERT INTO catalogos (nombre) VALUES (?)", (nombre,))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def listar_catalogos() -> list[dict]:
    with closing(conectar()) as conn:
        rows = conn.execute(
            "SELECT id, nombre FROM catalogos ORDER BY nombre"
        ).fetchall()
    return [{"id": r["id"], "nombre": r["nombre"]} for r in rows]


def eliminar_catalogo(catalogo_id: int) -> bool:
    with closing(conectar()) as conn:
        conn.execute("DELETE FROM catalogos WHERE id=?", (catalogo_id,))
        conn.commit()
        ok = conn.execute("SELECT changes()").fetchone()[0] > 0
    return ok


def renombrar_catalogo(catalogo_id: int, nuevo_nombre: str) -> bool:
    try:
        with closing(conectar()) as conn:
            conn.execute(
                "UPDATE catalogos SET nombre=? WHERE id=?",
                (nuevo_nombre, catalogo_id),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


# ─── TELAS ───────────────────────────────────────────────────────────────────

def agregar_tela(catalogo_id: int, nombre: str, ruta_img: str) -> bool:
    """
    Lee el archivo de imagen y guarda los bytes en SQLite.
    """
    try:
        print(f"[db] agregar_tela llamado")
        print(f"[db]   catalogo_id = {catalogo_id}")
        print(f"[db]   nombre      = '{nombre}'")
        print(f"[db]   ruta_img    = '{ruta_img}'")

        ruta_normalizada = os.path.normpath(ruta_img.strip()) if ruta_img else ""
        print(f"[db]   ruta_norm   = '{ruta_normalizada}'")
        print(f"[db]   existe      = {os.path.isfile(ruta_normalizada)}")

        if not ruta_normalizada or not os.path.isfile(ruta_normalizada):
            print("[db] ERROR: archivo no encontrado")
            return False

        with open(ruta_normalizada, "rb") as f:
            blob = f.read()
        ext = os.path.splitext(ruta_normalizada)[1].lower().lstrip(".")
        print(f"[db]   blob size   = {len(blob)} bytes")
        print(f"[db]   extension   = '{ext}'")

        # Verificar que la tabla telas tiene las columnas correctas
        with closing(conectar()) as conn:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(telas)").fetchall()]
            print(f"[db]   columnas telas = {cols}")

            conn.execute(
                "INSERT INTO telas (catalogo_id, nombre, imagen_blob, extension) "
                "VALUES (?, ?, ?, ?)",
                (catalogo_id, nombre, blob, ext),
            )
            conn.commit()
            print("[db] INSERT exitoso")
            return True

    except Exception as ex:
        import traceback
        print(f"[db] EXCEPCION en agregar_tela: {type(ex).__name__}: {ex}")
        traceback.print_exc()
        return False


def listar_telas(catalogo_id: int) -> list[dict]:
    """Retorna id, nombre, imagen_blob, extension."""
    with closing(conectar()) as conn:
        rows = conn.execute(
            "SELECT id, nombre, imagen_blob, extension "
            "FROM telas WHERE catalogo_id=? ORDER BY nombre",
            (catalogo_id,),
        ).fetchall()
    return [
        {
            "id":          r["id"],
            "nombre":      r["nombre"],
            "imagen_blob": r["imagen_blob"],
            "extension":   r["extension"],
        }
        for r in rows
    ]


def eliminar_tela(tela_id: int) -> bool:
    with closing(conectar()) as conn:
        conn.execute("DELETE FROM telas WHERE id=?", (tela_id,))
        conn.commit()
        ok = conn.execute("SELECT changes()").fetchone()[0] > 0
    return ok