import sqlite3

def conectar():
    return sqlite3.connect("database.db")


def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


def registrar_usuario(usuario, password):
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO usuarios (usuario, password) VALUES (?, ?)",
            (usuario, password)
        )

        conn.commit()
        conn.close()
        return True
    except:
        return False


def login_usuario(usuario, password):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM usuarios WHERE usuario=? AND password=?",
        (usuario, password)
    )

    res = cursor.fetchone()
    conn.close()

    return res is not None


def actualizar_password(usuario, nueva_password):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE usuarios SET password=? WHERE usuario=?",
        (nueva_password, usuario)
    )

    conn.commit()
    actualizado = cursor.rowcount > 0
    conn.close()

    return actualizado