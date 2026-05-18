import flet as ft
import os
import subprocess
import sys
import db

RUTA_TELAS = "telas"
RUTA_MODELOS = "modelos"


class App:

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "SofaLab 3D"
        self.page.scroll = "auto"
        self.page.bgcolor = "#f5f5f5"

        self.usuario = None

        self.contenido = ft.Container(padding=20)
        self.nav = ft.Row(alignment="spaceBetween")

        self.page.add(
            ft.Column([
                self.nav,
                self.contenido
            ])
        )

        db.crear_tablas()

        self.actualizar_nav()
        self.inicio()

    # ---------------- NAV ----------------
    def actualizar_nav(self):

        if self.usuario:
            self.nav.controls = [
                ft.TextButton("Inicio", on_click=lambda e: self.inicio()),
                ft.TextButton("Telas", on_click=lambda e: self.modulo_telas()),
                ft.TextButton("Modelos 3D", on_click=lambda e: self.modulo_3d()),
                ft.Text(f"👤 {self.usuario}"),
                ft.TextButton("Perfil", on_click=lambda e: self.perfil()),
                ft.TextButton("Salir", on_click=self.logout)
            ]
        else:
            self.nav.controls = [
                ft.TextButton("Inicio", on_click=lambda e: self.inicio()),
                ft.TextButton("Login", on_click=self.login)
            ]

        self.page.update()

    # ---------------- INICIO ----------------
    def inicio(self):
        self.contenido.content = ft.Column([
            ft.Text("SofaLab 3D", size=32, weight="bold"),
            ft.Text("Configurador de muebles y catálogo de telas"),
        ])
        self.page.update()

    # ---------------- LOGIN ----------------
    def login(self, e=None):

        usuario = ft.TextField(label="Usuario")
        password = ft.TextField(label="Contraseña", password=True)
        msg = ft.Text(color="red")

        def entrar(e):
            if db.login_usuario(usuario.value, password.value):
                self.usuario = usuario.value
                self.actualizar_nav()
                self.inicio()
            else:
                msg.value = "Datos incorrectos"
                self.page.update()

        self.contenido.content = ft.Column([
            ft.Text("Iniciar sesión", size=28, weight="bold"),
            usuario,
            password,
            msg,
            ft.ElevatedButton("Ingresar", on_click=entrar),
            ft.Row([
                ft.TextButton("Registrarse", on_click=self.registro),
                ft.TextButton("Recuperar contraseña", on_click=self.recuperar)
            ])
        ], width=400)

        self.page.update()

    # ---------------- REGISTRO ----------------
    def registro(self, e):

        usuario = ft.TextField(label="Usuario")
        password = ft.TextField(label="Contraseña", password=True)
        msg = ft.Text()

        def crear(e):
            if db.registrar_usuario(usuario.value, password.value):
                msg.value = "Usuario creado"
            else:
                msg.value = "Ya existe"
            self.page.update()

        self.contenido.content = ft.Column([
            ft.Text("Registro", size=28),
            usuario,
            password,
            msg,
            ft.ElevatedButton("Crear cuenta", on_click=crear),
            ft.TextButton("Volver", on_click=self.login)
        ])

        self.page.update()

    # ---------------- RECUPERAR ----------------
    def recuperar(self, e):

        usuario = ft.TextField(label="Usuario")
        nueva = ft.TextField(label="Nueva contraseña", password=True)
        msg = ft.Text()

        def cambiar(e):
            if db.actualizar_password(usuario.value, nueva.value):
                msg.value = "Contraseña actualizada"
            else:
                msg.value = "Usuario no encontrado"
            self.page.update()

        self.contenido.content = ft.Column([
            ft.Text("Recuperar contraseña", size=28),
            usuario,
            nueva,
            msg,
            ft.ElevatedButton("Actualizar", on_click=cambiar),
            ft.TextButton("Volver", on_click=self.login)
        ])

        self.page.update()

    # ---------------- PERFIL ----------------
    def perfil(self):
        self.contenido.content = ft.Column([
            ft.Text("Perfil", size=28),
            ft.Text(f"Usuario: {self.usuario}")
        ])
        self.page.update()

    def logout(self, e):
        self.usuario = None
        self.actualizar_nav()
        self.inicio()

    # ---------------- TELAS (AHORA SÍ BONITO Y FUNCIONANDO) ----------------
    def modulo_telas(self):

        def card(ruta_img, nombre):
            return ft.Container(
                width=160,
                height=180,
                bgcolor="white",
                border_radius=15,
                padding=10,
                shadow=ft.BoxShadow(blur_radius=10, color="black26"),
                content=ft.Column([
                    ft.Image(src=ruta_img, width=140, height=120),
                    ft.Text(nombre, size=12, weight="bold", text_align="center")
                ], alignment="center"),
                animate_scale=300,
                on_hover=lambda e: (
                    setattr(e.control, "scale", 1.1 if e.data == "true" else 1),
                    self.page.update()
                )
            )

        contenido = []

        if not os.path.exists(RUTA_TELAS):
            self.contenido.content = ft.Text("No existe carpeta telas")
            self.page.update()
            return

        for item in os.listdir(RUTA_TELAS):
            ruta = os.path.join(RUTA_TELAS, item)

            # 📁 CARPETAS
            if os.path.isdir(ruta):
                cards = []

                for img in os.listdir(ruta):
                    ruta_img = os.path.join(ruta, img)

                    if os.path.isfile(ruta_img):
                        cards.append(card(ruta_img, img))

                contenido.append(
                    ft.Container(
                        bgcolor="#eeeeee",
                        padding=15,
                        border_radius=10,
                        content=ft.Column([
                            ft.Text(item, size=22, weight="bold"),
                            ft.Row(cards, wrap=True, spacing=10)
                        ])
                    )
                )

            # 🖼️ IMÁGENES SUELTAS
            elif os.path.isfile(ruta):
                contenido.append(card(ruta, item))

        self.contenido.content = ft.Column([
            ft.Text("🎨 Catálogo de Telas", size=30, weight="bold"),
            ft.Divider(),
            *contenido
        ], spacing=20)

        self.page.update()

    # ---------------- 3D ----------------
    def modulo_3d(self):

        modelos = []

        if not os.path.exists(RUTA_MODELOS):
            self.contenido.content = ft.Text("No existe carpeta modelos")
            self.page.update()
            return

        for archivo in os.listdir(RUTA_MODELOS):
            if archivo.endswith(".glb"):
                modelos.append(
                    ft.Container(
                        padding=10,
                        bgcolor="white",
                        border_radius=10,
                        content=ft.Row([
                            ft.Text(archivo),
                            ft.ElevatedButton(
                                "Abrir",
                                on_click=lambda e, m=archivo: self.abrir_modelo(m)
                            )
                        ])
                    )
                )

        self.contenido.content = ft.Column([
            ft.Text("Visualización 3D", size=28),
            *modelos
        ])

        self.page.update()

    def abrir_modelo(self, modelo):
        subprocess.Popen([sys.executable, "main.py", modelo])


# ---------------- MAIN ----------------
def main(page: ft.Page):
    App(page)


if __name__ == "__main__":
    ft.app(target=main)