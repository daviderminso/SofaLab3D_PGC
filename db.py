import sqlite3
import hashlib
from contextlib import closing

DB = "sofalab.db"

CATALOGOS_INICIALES = ["Cuerina", "Veranera", "Nevada", "Turin", "Tornado"]


# ─── CONEXIÓN ────────────────────────────────────────────────────────────────

def conectar() -> sqlite3.Connection:
    """Abre la BD con foreign keys activas y row_factory para dicts."""
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row          # permite acceso por nombre de columna
    return conn


# ─── HASH ────────────────────────────────────────────────────────────────────

def _hash(pwd: str) -> str:
    """SHA-256 de la contraseña.  Nunca guardes texto plano."""
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
            ruta_img    TEXT NOT NULL,
            FOREIGN KEY (catalogo_id) REFERENCES catalogos(id) ON DELETE CASCADE
        )
        """)

        # Índice para acelerar listar_telas()
        c.execute("""
        CREATE INDEX IF NOT EXISTS idx_telas_catalogo
        ON telas(catalogo_id)
        """)

        # Catálogos iniciales
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
    try:
        with closing(conectar()) as conn:
            conn.execute(
                "INSERT INTO telas (catalogo_id, nombre, ruta_img) VALUES (?, ?, ?)",
                (catalogo_id, nombre, ruta_img),
            )
            conn.commit()
        return True
    except Exception:
        return False


def listar_telas(catalogo_id: int) -> list[dict]:
    with closing(conectar()) as conn:
        rows = conn.execute(
            "SELECT id, nombre, ruta_img FROM telas WHERE catalogo_id=? ORDER BY nombre",
            (catalogo_id,),
        ).fetchall()
    return [{"id": r["id"], "nombre": r["nombre"], "ruta_img": r["ruta_img"]} for r in rows]


def eliminar_tela(tela_id: int) -> bool:
    with closing(conectar()) as conn:
        conn.execute("DELETE FROM telas WHERE id=?", (tela_id,))
        conn.commit()
        ok = conn.execute("SELECT changes()").fetchone()[0] > 0
    return ok