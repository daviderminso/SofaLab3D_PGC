import flet as ft
import os
import subprocess
import sys
import db

RUTA_MODELOS = "modelos"

# ─── PALETA (idéntica al HTML) ────────────────────────────────────────────────
BG       = "#F7F4F0"
SURFACE  = "#FFFFFF"
SURFACE2 = "#F0EBE3"
NAV_BG   = "#1C1410"
ACCENT   = "#8B1A1A"
ACCENT2  = "#C8956C"
TEXT     = "#1C1410"
TEXT_SUB = "#7A6A5A"
TEXT_NAV = "#E8DDD0"
DANGER   = "#B03020"
SUCCESS  = "#2E7D52"
BORDER   = "#DDD5CA"
CARD_BG  = "#FFFFFF"
NAV_HOVER= "#2C1F18"
NAV_DIV  = "#2E2018"
HERO_BG  = "#1C1410"

PWD_MIN  = 6


# ─── HELPERS UI ──────────────────────────────────────────────────────────────

def borde(color=BORDER, width=1) -> ft.Border:
    lado = ft.BorderSide(width, color)
    return ft.Border(top=lado, bottom=lado, left=lado, right=lado)


def btn_primary(texto, on_click, width=None):
    return ft.ElevatedButton(
        texto, on_click=on_click, width=width,
        style=ft.ButtonStyle(
            bgcolor=ACCENT, color="white",
            shape=ft.RoundedRectangleBorder(radius=6),
            elevation=0,
        ),
    )


def btn_danger(texto, on_click):
    return ft.ElevatedButton(
        texto, on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor=DANGER, color="white",
            shape=ft.RoundedRectangleBorder(radius=6),
            elevation=0,
        ),
    )


def btn_ghost(texto, on_click):
    return ft.TextButton(
        texto, on_click=on_click,
        style=ft.ButtonStyle(color=ACCENT),
    )


def campo(label, password=False, hint=None, expand=False):
    return ft.TextField(
        label=label, password=password, hint_text=hint,
        bgcolor=SURFACE, border_color=BORDER,
        focused_border_color=ACCENT,
        label_style=ft.TextStyle(color=TEXT_SUB),
        color=TEXT, cursor_color=ACCENT,
        border_radius=6, expand=expand,
    )


def titulo(texto, size=26):
    return ft.Text(texto, size=size, weight="bold", color=TEXT)


def subtitulo(texto, size=13):
    return ft.Text(texto, size=size, color=TEXT_SUB)


def snack(page, msg, ok=True):
    page.snack_bar = ft.SnackBar(
        content=ft.Text(msg, color="white"),
        bgcolor=SUCCESS if ok else DANGER,
        duration=2500,
    )
    page.snack_bar.open = True
    page.update()


def section_label(texto):
    return ft.Text(
        texto.upper(), size=11, color=ACCENT2,
        weight="bold", style=ft.TextStyle(letter_spacing=3),
    )


def divider():
    return ft.Container(height=1, bgcolor=BORDER, margin=ft.Margin(left=0, right=0, top=0, bottom=0))


# ─── VALIDACIONES ────────────────────────────────────────────────────────────

def _validar_usuario(nombre: str) -> str | None:
    if not nombre:
        return "Completa todos los campos"
    if " " in nombre:
        return "El usuario no puede contener espacios"
    if len(nombre) < 3:
        return "El usuario debe tener al menos 3 caracteres"
    return None


def _validar_pwd(pwd: str) -> str | None:
    if not pwd:
        return "Completa todos los campos"
    if len(pwd) < PWD_MIN:
        return f"La contraseña debe tener al menos {PWD_MIN} caracteres"
    return None


# ─── COMPONENTES VISUALES ────────────────────────────────────────────────────

def stat_block(numero, label):
    """Bloque de estadística para la stats-bar."""
    return ft.Container(
        expand=True,
        padding=ft.Padding(left=0, right=0, top=16, bottom=16),
        content=ft.Column([
            ft.Text(numero, size=28, weight="bold", color=ACCENT2),
            ft.Text(label, size=10, color="#6E5E50", style=ft.TextStyle(letter_spacing=1)),
        ], horizontal_alignment="center", spacing=2),
    )


def badge(texto, accent=False):
    return ft.Container(
        bgcolor="#F5EAE0" if accent else SURFACE2,
        border_radius=20,
        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
        border=borde("#E8D0C0" if accent else BORDER),
        content=ft.Text(
            texto, size=11,
            color=ACCENT if accent else TEXT_SUB,
            weight="w500",
        ),
    )


def sec_item(icono, titulo_txt, desc):
    """Item de seguridad."""
    return ft.Container(
        bgcolor=SURFACE, border_radius=10,
        border=borde(), padding=20,
        width=260,
        content=ft.Column([
            ft.Text(icono, size=28),
            ft.Container(height=8),
            ft.Text(titulo_txt, size=13, weight="bold", color=TEXT),
            ft.Container(height=4),
            ft.Text(desc, size=11, color=TEXT_SUB, max_lines=4),
        ], spacing=0),
    )


def contact_card(icono, titulo_txt, *infos):
    lineas = [ft.Text(i, size=13, color=TEXT_SUB) for i in infos]
    return ft.Container(
        bgcolor=SURFACE, border_radius=12,
        border=borde(), padding=24,
        width=260,
        content=ft.Column([
            ft.Text(icono, size=28),
            ft.Container(height=10),
            ft.Text(titulo_txt, size=15, weight="bold", color=TEXT),
            ft.Container(height=4),
            *lineas,
        ], spacing=2),
    )


# ─── CUBO 3D ANIMADO (CSS-inspired via AnimatedRotation) ─────────────────────

def hero_cubo():
    """Cubo decorativo en el hero usando un Stack con caras estilizadas."""
    cara = lambda emoji, rot_y=0: ft.Container(
        width=110, height=110,
        bgcolor="#2A1010",
        border=ft.Border.all(1, "#7A5A3A"),
        border_radius=4,
        content=ft.Text(emoji, size=32, text_align="center"),
        alignment=ft.alignment.Alignment(0, 0),
    )
    # Simulamos el cubo como un stack de caras con offsets
    return ft.Container(
        width=200, height=200,
        content=ft.Stack([
            ft.Container(
                left=40, top=40,
                content=ft.Column([
                    ft.Row([cara("🛋️"), cara("🪑")], spacing=4),
                    ft.Row([cara("🎨"), cara("📐")], spacing=4),
                ], spacing=4),
            ),
        ]),
    )


# ─── APP ─────────────────────────────────────────────────────────────────────

class App:

    def __init__(self, page: ft.Page):
        self.page    = page
        self.usuario = None
        self._cubo_activo = False

        page.title   = "SofaLab 3D Studio"
        page.bgcolor = BG
        page.padding = 0
        page.fonts   = {}

        # Área de contenido principal con scroll
        self.contenido = ft.Container(
            expand=True, bgcolor=BG,
        )
        self._scroll_col = ft.Column(
            [self.contenido],
            expand=True, scroll="auto",
        )

        self.sidebar = ft.Container(
            width=220, bgcolor=NAV_BG,
            expand=False,
        )

        page.add(
            ft.Row(
                [self.sidebar, self._scroll_col],
                expand=True,
                vertical_alignment="start",
                spacing=0,
            )
        )

        db.crear_tablas()
        self._rebuild_sidebar()
        self.pantalla_inicio()

    # ─── SIDEBAR ─────────────────────────────────────────────────────────────

    def _nav_item(self, icono, texto, on_click, activo=False):
        return ft.Container(
            padding=ft.Padding(left=20, right=20, top=14, bottom=14),
            bgcolor=NAV_HOVER if activo else "transparent",
            on_click=on_click, ink=True,
            border=ft.Border(
                left=ft.BorderSide(3, ACCENT2) if activo else ft.BorderSide(3, "transparent")
            ),
            content=ft.Row([
                ft.Text(icono, size=16, width=20, text_align="center"),
                ft.Text(
                    texto, size=14,
                    color=TEXT_NAV if activo else "#9E8E80",
                    weight="bold" if activo else "normal",
                ),
            ], spacing=10),
        )

    def _rebuild_sidebar(self, activo=None):
        logo = ft.Container(
            padding=ft.Padding(left=20, right=20, top=24, bottom=16),
            border=ft.Border(bottom=ft.BorderSide(1, NAV_DIV)),
            content=ft.Column([
                ft.Text("SofaLab", size=20, weight="bold", color=TEXT_NAV, style=ft.TextStyle(letter_spacing=0.5)),
                ft.Text("3D STUDIO", size=9, color="#6E5E50", style=ft.TextStyle(letter_spacing=3)),
            ], spacing=2),
        )

        if self.usuario:
            nav_items = [
                logo,
                ft.Container(height=8),
                self._nav_item("🏠", "Inicio",     lambda e: self.pantalla_inicio(),  activo == "inicio"),
                self._nav_item("🎨", "Materiales", lambda e: self.pantalla_telas(),   activo == "telas"),
                self._nav_item("📦", "Modelos 3D", lambda e: self.pantalla_3d(),      activo == "3d"),
                self._nav_item("👤", "Mi perfil",  lambda e: self.pantalla_perfil(),  activo == "perfil"),
                self._nav_item("👥", "Nosotros",   lambda e: self.pantalla_nosotros(),activo == "nosotros"),
                self._nav_item("✉️", "Contacto",   lambda e: self.pantalla_contacto(),activo == "contacto"),
                ft.Container(expand=True),
                ft.Container(height=1, bgcolor=NAV_DIV),
                ft.Container(
                    padding=ft.Padding(left=20, right=20, top=16, bottom=16),
                    content=ft.Column([
                        ft.Text(self.usuario, size=13, color=TEXT_NAV, weight="bold"),
                        ft.Text("● Activo", size=10, color="#6E5E50"),
                    ], spacing=2),
                ),
                ft.Container(
                    padding=ft.Padding(left=20, right=20, top=10, bottom=10),
                    on_click=self._logout, ink=True,
                    content=ft.Row([
                        ft.Text("🚪", size=15),
                        ft.Text("Cerrar sesión", size=13, color="#A05040"),
                    ], spacing=8),
                ),
            ]
        else:
            nav_items = [
                logo,
                ft.Container(height=8),
                self._nav_item("🏠", "Inicio",     lambda e: self.pantalla_inicio(), activo == "inicio"),
                self._nav_item("👥", "Nosotros",   lambda e: self.pantalla_nosotros(), activo == "nosotros"),
                self._nav_item("✉️", "Contacto",   lambda e: self.pantalla_contacto(), activo == "contacto"),
                self._nav_item("🔑", "Ingresar",   lambda e: self.pantalla_login(),  activo == "login"),
            ]

        self.sidebar.content = ft.Column(nav_items, spacing=0, expand=True)
        self.page.update()

    # ─── HELPERS ─────────────────────────────────────────────────────────────

    def _set(self, widget):
        self._cubo_activo = False   # detiene animación si estaba corriendo
        self.contenido.content = widget
        self.page.update()

    def _reset_bg(self):
        """Restaura el fondo crema al navegar fuera del inicio logueado."""
        self.contenido.bgcolor = BG

    def _logout(self, e=None):
        self.usuario = None
        self._rebuild_sidebar()
        self.pantalla_inicio()

    # ─── INICIO ──────────────────────────────────────────────────────────────

    def pantalla_inicio(self):
        self._rebuild_sidebar("inicio")
        if self.usuario:
            self.contenido.bgcolor = HERO_BG
            self._set(self._build_home_logueado())
        else:
            self.contenido.bgcolor = BG
            self._set(self._build_home_publico())

    def _build_home_publico(self):
        """Página de inicio completa fiel al HTML: hero, stats, módulos, about, seguridad, equipo, contacto, footer."""

        # ── HERO ──────────────────────────────────────────────────────────────
        hero = ft.Container(
            bgcolor=HERO_BG,
            padding=ft.Padding(left=48, right=48, top=64, bottom=64),
            content=ft.Row([
                # Contenido izquierdo
                ft.Column([
                    # Badge
                    ft.Container(
                        bgcolor="#3D1010",
                        border_radius=20,
                        padding=ft.Padding(left=14, right=14, top=6, bottom=6),
                        border=ft.Border.all(1, "#6B1A1A"),
                        content=ft.Text("✦ Software profesional de tapicería 3D",
                                        size=11, color="#F5C4A0", style=ft.TextStyle(letter_spacing=0.5)),
                    ),
                    ft.Container(height=16),
                    # Título
                    ft.Column([
                        ft.Text("SofaLab", size=52, weight="bold", color="white"),
                        ft.Text("3D Studio", size=52, weight="bold", color=ACCENT2),
                    ], spacing=0),
                    ft.Container(height=12),
                    # Subtítulo
                    ft.Text(
                        "Diseña, visualiza y cotiza muebles tapizados con\ntecnología 3D. "
                        "Gestiona materiales, modelos y\npresupuestos desde un solo lugar.",
                        size=15, color="#B8A898",
                    ),
                    ft.Container(height=28),
                    # Botones
                    ft.Row([
                        ft.ElevatedButton(
                            "🚀 Comenzar ahora",
                            on_click=lambda e: self.pantalla_login(),
                            style=ft.ButtonStyle(
                                bgcolor=ACCENT, color="white",
                                shape=ft.RoundedRectangleBorder(radius=8),
                                elevation=0,
                                padding=ft.Padding(left=24, right=24, top=14, bottom=14),
                            ),
                        ),
                        ft.OutlinedButton(
                            "📦 Ver modelos 3D",
                            on_click=lambda e: self.pantalla_login(),
                            style=ft.ButtonStyle(
                                color=TEXT_NAV,
                                side=ft.BorderSide(1, "#4D4440"),
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.Padding(left=24, right=24, top=14, bottom=14),
                            ),
                        ),
                    ], spacing=12),
                ], spacing=0),
                # Decoración cubo
                ft.Container(
                    width=220, height=220,
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                width=100, height=100,
                                bgcolor="#2A1010",
                                border=ft.Border.all(2, "#7A5A3A"),
                                border_radius=4,
                                content=ft.Text("🛋️", size=36, text_align="center"),
                                alignment=ft.alignment.Alignment(0, 0),
                            ),
                            ft.Container(
                                width=100, height=100,
                                bgcolor="#251010",
                                border=ft.Border.all(2, "#7A5A3A"),
                                border_radius=4,
                                content=ft.Text("🪑", size=36, text_align="center"),
                                alignment=ft.alignment.Alignment(0, 0),
                            ),
                        ], spacing=6),
                        ft.Row([
                            ft.Container(
                                width=100, height=100,
                                bgcolor="#2A1E12",
                                border=ft.Border.all(2, "#7A5A3A"),
                                border_radius=4,
                                content=ft.Text("🎨", size=36, text_align="center"),
                                alignment=ft.alignment.Alignment(0, 0),
                            ),
                            ft.Container(
                                width=100, height=100,
                                bgcolor="#251B10",
                                border=ft.Border.all(2, "#7A5A3A"),
                                border_radius=4,
                                content=ft.Text("📐", size=36, text_align="center"),
                                alignment=ft.alignment.Alignment(0, 0),
                            ),
                        ], spacing=6),
                    ], spacing=6),
                ),
            ], spacing=0, vertical_alignment="center"),
        )

        # ── STATS BAR ─────────────────────────────────────────────────────────
        stats = ft.Container(
            bgcolor=HERO_BG,
            border=ft.Border(bottom=ft.BorderSide(1, NAV_DIV)),
            padding=ft.Padding(left=48, right=48, top=4, bottom=4),
            content=ft.Row([
                stat_block("5", "CATÁLOGOS DE TELAS"),
                ft.Container(width=1, bgcolor=NAV_DIV),
                stat_block("12", "MODELOS 3D"),
                ft.Container(width=1, bgcolor=NAV_DIV),
                stat_block("80+", "MATERIALES"),
                ft.Container(width=1, bgcolor=NAV_DIV),
                stat_block("1", "USUARIOS ACTIVOS"),
            ], spacing=0),
        )

        # ── MÓDULOS ───────────────────────────────────────────────────────────
        modulos = ft.Container(
            padding=48,
            content=ft.Column([
                section_label("Módulos del sistema"),
                ft.Container(height=6),
                titulo("Todo lo que necesitas", 28),
                ft.Container(height=6),
                subtitulo("Herramientas diseñadas para el flujo real de un taller de tapicería profesional."),
                ft.Container(height=28),
                ft.Row([
                    self._feature_card("🎨", "Biblioteca de Materiales",
                        "Catálogos organizados de telas, cuero y texturas. Agrega imágenes y filtra por colección.",
                        "Cuerina · Veranera · Nevada",
                        lambda e: self.pantalla_login()),
                    self._feature_card("📦", "Visualización 3D",
                        "Carga modelos .GLB, .EGG o .GLTF y explóralos con rotación libre, zoom y luz ambiental.",
                        "Panda3D · GLB · GLTF",
                        lambda e: self.pantalla_login()),
                    self._feature_card("🧾", "Cotización",
                        "Genera presupuestos detallados por cliente, incluyendo materiales y tiempos de entrega.",
                        "Próximamente",
                        None),
                    self._feature_card("📊", "Panel de Control",
                        "Vista general del negocio: pedidos activos, materiales disponibles y estadísticas.",
                        "Próximamente",
                        None),
                ], wrap=True, spacing=16),
            ], spacing=4),
        )

        # ── ABOUT ─────────────────────────────────────────────────────────────
        about = ft.Container(
            padding=48,
            content=ft.Column([
                section_label("Acerca del proyecto"),
                ft.Container(height=6),
                titulo("¿Qué es SofaLab 3D?", 28),
                ft.Container(height=6),
                subtitulo("Una solución de escritorio construida para modernizar los talleres de tapicería con tecnología accesible."),
                ft.Container(height=24),
                ft.Row([
                    # Info general
                    ft.Container(
                        width=340,
                        bgcolor=SURFACE, border_radius=12,
                        border=borde(), padding=24,
                        content=ft.Column([
                            ft.Text("📋 Información general", size=13, weight="bold", color=TEXT),
                            ft.Container(height=12),
                            self._info_row("Nombre",      "SofaLab 3D Studio"),
                            self._info_row("Tipo",        "Aplicación de escritorio"),
                            self._info_row("Plataforma",  "Windows / Linux / macOS"),
                            self._info_row("Base de datos","SQLite (local)"),
                            self._info_row("Versión",     "1.0.0 Beta"),
                        ], spacing=0),
                    ),
                    # Tecnologías
                    ft.Container(
                        width=340,
                        bgcolor=SURFACE, border_radius=12,
                        border=borde(), padding=24,
                        content=ft.Column([
                            ft.Text("🛠️ Tecnologías utilizadas", size=13, weight="bold", color=TEXT),
                            ft.Container(height=12),
                            ft.Row([
                                badge("Python 3", accent=True),
                                badge("Flet", accent=True),
                                badge("Panda3D", accent=True),
                                badge("SQLite"),
                            ], wrap=True, spacing=6),
                            ft.Row([
                                badge("Flutter Engine"),
                                badge("OpenGL"),
                                badge("SHA-256"),
                                badge("hashlib"),
                            ], wrap=True, spacing=6),
                            ft.Container(height=16),
                            ft.Text("🎯 Objetivo", size=13, weight="bold", color=TEXT),
                            ft.Container(height=6),
                            ft.Text(
                                "Digitalizar la gestión de talleres de tapicería, "
                                "permitiendo a artesanos y diseñadores visualizar sus "
                                "creaciones en 3D antes de producirlas.",
                                size=13, color=TEXT_SUB,
                            ),
                        ], spacing=0),
                    ),
                ], spacing=20),
            ], spacing=4),
        )

        # ── SEGURIDAD ─────────────────────────────────────────────────────────
        seguridad = ft.Container(
            padding=48,
            content=ft.Column([
                section_label("Seguridad del sistema"),
                ft.Container(height=6),
                titulo("Tus datos, protegidos", 28),
                ft.Container(height=6),
                subtitulo("Implementamos las mejores prácticas de seguridad para una aplicación de escritorio local."),
                ft.Container(height=24),
                ft.Row([
                    sec_item("🔐", "Contraseñas cifradas",
                             "SHA-256 hash en cada contraseña. Nunca se guarda texto plano en la base de datos."),
                    sec_item("🗃️", "BD local y privada",
                             "SQLite sin servidor. Tus datos nunca salen de tu computador ni pasan por internet."),
                    sec_item("🔗", "Integridad referencial",
                             "Foreign keys con CASCADE aseguran que no queden datos huérfanos al eliminar catálogos."),
                ], spacing=14, wrap=True),
                ft.Container(height=14),
                ft.Row([
                    sec_item("✅", "Validación de entrada",
                             "Cada campo valida formato, longitud y caracteres antes de tocar la base de datos."),
                    sec_item("🔒", "Sesión protegida",
                             "Sin sesión activa no se accede a materiales ni modelos. Redirección automática al login."),
                    sec_item("🧩", "Conexiones seguras",
                             "Context managers garantizan que cada conexión a SQLite se cierre aunque haya errores."),
                ], spacing=14, wrap=True),
            ], spacing=4),
        )

        # ── EQUIPO ────────────────────────────────────────────────────────────
        equipo = ft.Container(
            padding=48,
            content=ft.Column([
                section_label("Equipo de desarrollo"),
                ft.Container(height=6),
                titulo("Nosotros", 28),
                ft.Container(height=6),
                subtitulo("Estudiantes de ingeniería apasionados por unir tecnología y diseño industrial."),
                ft.Container(height=24),
                ft.Row([
                    self._team_card("D1", "#8B1A1A", ACCENT2,
                                    "Desarrollador 1", "Lead Developer · Backend & DB",
                                    "Responsable de la arquitectura, base de datos, seguridad y lógica de negocio del sistema."),
                    self._team_card("D2", ACCENT2, "#8B4513",
                                    "Desarrollador 2", "Frontend & 3D Engineer",
                                    "Diseño de interfaz, visualización 3D con Panda3D y experiencia de usuario del software."),
                ], spacing=20, wrap=True),
                ft.Container(height=20),
                ft.Container(
                    bgcolor=SURFACE, border_radius=12,
                    border=borde(), padding=24,
                    content=ft.Row([
                        ft.Text("🏛️", size=36),
                        ft.Container(width=16),
                        ft.Column([
                            ft.Text("Universidad de formación", size=15, weight="bold", color=TEXT),
                            ft.Text("Proyecto de grado en Ingeniería de Sistemas · 2025", size=13, color=TEXT_SUB),
                            ft.Text("Agrega aquí el nombre de tu universidad ✏️", size=12, color=ACCENT, weight="w500"),
                        ], spacing=4),
                    ], vertical_alignment="center"),
                ),
            ], spacing=4),
        )

        # ── CONTACTO ──────────────────────────────────────────────────────────
        contacto = ft.Container(
            padding=48,
            content=ft.Column([
                section_label("Contacto"),
                ft.Container(height=6),
                titulo("¿Tienes alguna consulta?", 28),
                ft.Container(height=6),
                subtitulo("Puedes comunicarte con el equipo de desarrollo directamente."),
                ft.Container(height=24),
                ft.Row([
                    contact_card("📧", "Correo electrónico",
                                 "correo@universidad.edu.co",
                                 "correo2@universidad.edu.co"),
                    contact_card("💻", "Repositorio del proyecto",
                                 "github.com/usuario/sofalab3d"),
                    contact_card("📍", "Ubicación",
                                 "Colombia · Facultad de Ingeniería"),
                    contact_card("🕐", "Horario de atención",
                                 "Lunes a Viernes · 8am – 6pm"),
                ], spacing=16, wrap=True),
            ], spacing=4),
        )

        # ── FOOTER ────────────────────────────────────────────────────────────
        footer = ft.Container(
            bgcolor=HERO_BG,
            padding=ft.Padding(left=48, right=48, top=28, bottom=28),
            content=ft.Row([
                ft.Column([
                    ft.Row([
                        ft.Text("SofaLab ", size=18, weight="bold", color=TEXT_NAV),
                        ft.Text("3D", size=18, weight="bold", color=ACCENT2),
                    ], spacing=0),
                    ft.Text("Software de tapicería con visualización 3D",
                            size=12, color="#6E5E50"),
                ], spacing=4),
                ft.Column([
                    ft.Text("Hecho con ❤️ en Python · Flet · Panda3D",
                            size=12, color="#6E5E50", text_align="right"),
                    ft.Text("© 2025 SofaLab 3D · Proyecto universitario",
                            size=12, color="#6E5E50", text_align="right"),
                ], spacing=4, horizontal_alignment="end"),
            ], alignment="spaceBetween"),
        )

        return ft.Column([
            hero,
            stats,
            modulos,
            divider(),
            about,
            divider(),
            seguridad,
            divider(),
            equipo,
            divider(),
            contacto,
            footer,
        ], spacing=0)

    def _build_home_logueado(self):
        """Pantalla de inicio para usuario autenticado."""
        import asyncio

        # ── Cubo animado ──────────────────────────────────────────────────────
        CARAS = ["🛋️", "🪑", "🎨", "📐", "✨", "💼"]
        cara_txt = ft.Text(CARAS[0], size=52, text_align="center")
        cara_lbl = ft.Text("tapicería 3D", size=11, color="#9E8E80", text_align="center")

        cubo = ft.Container(
            width=140, height=140,
            bgcolor="#2C1A10",
            border_radius=16,
            border=ft.Border.all(2, "#7A5A3A"),
            content=ft.Column([
                cara_txt,
                ft.Container(height=6),
                cara_lbl,
            ], alignment="center", horizontal_alignment="center", spacing=0),
        )

        self._cubo_activo = True

        async def animar_cubo():
            labels = ["tapicería 3D", "modelos 3D", "materiales", "diseño", "detalles", "gestión"]
            i = 0
            while self._cubo_activo:
                await asyncio.sleep(1.2)
                i = (i + 1) % len(CARAS)
                cara_txt.value = CARAS[i]
                cara_lbl.value = labels[i]
                try:
                    self.page.update()
                except Exception:
                    break

        self.page.run_task(animar_cubo)

        # ── Hero ──────────────────────────────────────────────────────────────
        hero = ft.Container(
            bgcolor=HERO_BG,
            padding=ft.Padding(left=48, right=48, top=56, bottom=56),
            content=ft.Row([
                # Columna izquierda
                ft.Column([
                    ft.Container(
                        bgcolor="#3D1010",
                        border_radius=20,
                        padding=ft.Padding(left=14, right=14, top=6, bottom=6),
                        border=ft.Border.all(1, "#6B1A1A"),
                        content=ft.Text("✦ Panel de usuario", size=11, color="#F5C4A0",
                                        style=ft.TextStyle(letter_spacing=0.5)),
                        width=160,
                    ),
                    ft.Container(height=16),
                    ft.Text(f"Bienvenido,", size=20, color="#B8A898"),
                    ft.Text(f"{self.usuario}!", size=42, weight="bold", color="white"),
                    ft.Container(height=8),
                    ft.Text("¿Qué deseas gestionar hoy?", size=15, color="#B8A898"),
                    ft.Container(height=28),
                    ft.Row([
                        self._home_card_hero("🎨", "Materiales",
                                             "Catálogos de telas y texturas",
                                             lambda e: self.pantalla_telas()),
                        self._home_card_hero("📦", "Modelos 3D",
                                             "Explora y rota modelos",
                                             lambda e: self.pantalla_3d()),
                        self._home_card_hero("👤", "Mi Perfil",
                                             "Configuración de cuenta",
                                             lambda e: self.pantalla_perfil()),
                    ], spacing=14, wrap=True),
                ], spacing=0),
                # Cubo animado
                ft.Container(
                    padding=ft.Padding(left=40, right=0, top=0, bottom=0),
                    content=ft.Column([
                        cubo,
                        ft.Container(height=12),
                        ft.Text("Vista previa", size=10, color="#6E5E50",
                                 text_align="center"),
                    ], horizontal_alignment="center", spacing=0),
                ),
            ], spacing=40, vertical_alignment="center"),
        )

        stats = ft.Container(
            bgcolor=HERO_BG,
            border=ft.Border(bottom=ft.BorderSide(1, NAV_DIV)),
            padding=ft.Padding(left=48, right=48, top=4, bottom=4),
            content=ft.Row([
                stat_block(str(len(db.listar_catalogos())), "CATÁLOGOS"),
                ft.Container(width=1, bgcolor=NAV_DIV),
                stat_block("1", "USUARIO ACTIVO"),
            ], spacing=0),
        )
        relleno = ft.Container(bgcolor=HERO_BG, expand=True)
        return ft.Column([hero, stats, relleno], spacing=0, expand=True)

    def _home_card_hero(self, icono, tit, desc, on_click):
        return ft.Container(
            width=220, height=130,
            bgcolor="#2C1F18",
            border_radius=12,
            border=ft.Border.all(1, "#3D2E26"),
            padding=20, on_click=on_click, ink=True,
            content=ft.Column([
                ft.Text(icono, size=28),
                ft.Text(tit, size=14, weight="bold", color=TEXT_NAV),
                ft.Text(desc, size=11, color="#9E8E80"),
            ], spacing=5),
        )

    # ── Feature Card ─────────────────────────────────────────────────────────

    def _feature_card(self, icono, tit, desc, tag, on_click):
        return ft.Container(
            width=240,
            bgcolor=SURFACE, border_radius=12,
            border=borde(), padding=28,
            on_click=on_click, ink=bool(on_click),
            content=ft.Column([
                ft.Container(
                    width=52, height=52, border_radius=12,
                    bgcolor=SURFACE2,
                    content=ft.Text(icono, size=24, text_align="center"),
                    alignment=ft.alignment.Alignment(0, 0),
                ),
                ft.Container(height=14),
                ft.Text(tit, size=16, weight="bold", color=TEXT),
                ft.Container(height=4),
                ft.Text(desc, size=13, color=TEXT_SUB),
                ft.Container(height=12),
                ft.Container(
                    bgcolor="#F5EAE0", border_radius=20,
                    padding=ft.Padding(left=10, right=10, top=3, bottom=3),
                    content=ft.Text(tag, size=11, color=ACCENT, weight="w500"),
                ),
            ], spacing=0),
        )

    # ── Info Row ─────────────────────────────────────────────────────────────

    def _info_row(self, key, val):
        return ft.Container(
            border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
            padding=ft.Padding(left=0, right=0, top=8, bottom=8),
            content=ft.Row([
                ft.Text(key, size=13, color=TEXT_SUB, width=110),
                ft.Text(val, size=13, color=TEXT, weight="w500"),
            ]),
        )

    # ── Team Card ────────────────────────────────────────────────────────────

    def _team_card(self, initials, color1, color2, nombre, rol, bio):
        return ft.Container(
            width=380,
            bgcolor=SURFACE, border_radius=12,
            border=borde(), padding=28,
            content=ft.Row([
                ft.Container(
                    width=64, height=64, border_radius=12,
                    gradient=ft.LinearGradient(
                        colors=[color1, color2],
                        begin=ft.alignment.Alignment(-1, -1),
                        end=ft.alignment.Alignment(1, 1),
                    ),
                    content=ft.Text(initials, size=22, weight="bold", color="white",
                                    text_align="center"),
                    alignment=ft.alignment.Alignment(0, 0),
                ),
                ft.Container(width=16),
                ft.Column([
                    ft.Text(nombre, size=16, weight="bold", color=TEXT),
                    ft.Text(rol, size=12, color=ACCENT, weight="w500"),
                    ft.Container(height=4),
                    ft.Text(bio, size=12, color=TEXT_SUB),
                    ft.Container(height=8),
                    ft.Text("🎓 Universidad · Ingeniería de Sistemas", size=11, color=TEXT_SUB),
                ], spacing=2),
            ], vertical_alignment="start"),
        )

    # ─── PANTALLAS DE NAVEGACIÓN (nosotros, contacto, perfil) ────────────────

    def pantalla_nosotros(self):
        self._reset_bg()
        self._rebuild_sidebar("nosotros")
        self._set(ft.Container(
            padding=48,
            content=ft.Column([
                section_label("Equipo de desarrollo"),
                ft.Container(height=6),
                titulo("Nosotros", 28),
                ft.Container(height=6),
                subtitulo("Estudiantes de ingeniería apasionados por unir tecnología y diseño industrial."),
                ft.Container(height=28),
                ft.Row([
                    self._team_card("D1", "#8B1A1A", ACCENT2,
                                    "Desarrollador 1", "Lead Developer · Backend & DB",
                                    "Responsable de la arquitectura, base de datos, seguridad y lógica de negocio del sistema."),
                    self._team_card("D2", ACCENT2, "#8B4513",
                                    "Desarrollador 2", "Frontend & 3D Engineer",
                                    "Diseño de interfaz, visualización 3D con Panda3D y experiencia de usuario del software."),
                ], spacing=20, wrap=True),
                ft.Container(height=20),
                ft.Container(
                    bgcolor=SURFACE, border_radius=12,
                    border=borde(), padding=24,
                    content=ft.Row([
                        ft.Text("🏛️", size=36),
                        ft.Container(width=16),
                        ft.Column([
                            ft.Text("Universidad de formación", size=15, weight="bold", color=TEXT),
                            ft.Text("Proyecto de grado en Ingeniería de Sistemas · 2025", size=13, color=TEXT_SUB),
                            ft.Text("Agrega aquí el nombre de tu universidad ✏️", size=12, color=ACCENT, weight="w500"),
                        ], spacing=4),
                    ], vertical_alignment="center"),
                ),
            ], spacing=4),
        ))

    def pantalla_contacto(self):
        self._reset_bg()
        self._rebuild_sidebar("contacto")
        self._set(ft.Container(
            padding=48,
            content=ft.Column([
                section_label("Contacto"),
                ft.Container(height=6),
                titulo("¿Tienes alguna consulta?", 28),
                ft.Container(height=6),
                subtitulo("Puedes comunicarte con el equipo de desarrollo directamente."),
                ft.Container(height=28),
                ft.Row([
                    contact_card("📧", "Correo electrónico",
                                 "correo@universidad.edu.co",
                                 "correo2@universidad.edu.co"),
                    contact_card("💻", "Repositorio del proyecto",
                                 "github.com/usuario/sofalab3d"),
                    contact_card("📍", "Ubicación",
                                 "Colombia · Facultad de Ingeniería"),
                    contact_card("🕐", "Horario de atención",
                                 "Lunes a Viernes · 8am – 6pm"),
                ], spacing=16, wrap=True),
            ], spacing=4),
        ))

    def pantalla_perfil(self):
        self._reset_bg()
        self._rebuild_sidebar("perfil")
        if not self.usuario:
            self.pantalla_login()
            return

        pwd     = campo("Nueva contraseña", password=True)
        pwd2    = campo("Confirmar nueva contraseña", password=True)
        msg     = ft.Text("", size=12)

        def cambiar(e):
            err = _validar_pwd(pwd.value)
            if err:
                msg.value, msg.color = err, DANGER
                self.page.update()
                return
            if pwd.value != pwd2.value:
                msg.value, msg.color = "Las contraseñas no coinciden", DANGER
                self.page.update()
                return
            if db.actualizar_password(self.usuario, pwd.value):
                msg.value, msg.color = "Contraseña actualizada correctamente", SUCCESS
                pwd.value = pwd2.value = ""
            else:
                msg.value, msg.color = "Error al actualizar", DANGER
            self.page.update()

        self._set(ft.Container(
            padding=48,
            content=ft.Column([
                section_label("Mi perfil"),
                ft.Container(height=6),
                titulo("Configuración de cuenta", 28),
                ft.Container(height=24),
                ft.Container(
                    bgcolor=SURFACE, border_radius=12,
                    border=borde(), padding=28,
                    width=480,
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                width=64, height=64, border_radius=32,
                                gradient=ft.LinearGradient(
                                    colors=[ACCENT, ACCENT2],
                                    begin=ft.alignment.Alignment(-1, -1),
                                    end=ft.alignment.Alignment(1, 1),
                                ),
                                content=ft.Text(
                                    self.usuario[0].upper(),
                                    size=26, weight="bold", color="white", text_align="center",
                                ),
                                alignment=ft.alignment.Alignment(0, 0),
                            ),
                            ft.Container(width=16),
                            ft.Column([
                                ft.Text(self.usuario, size=18, weight="bold", color=TEXT),
                                ft.Text("● Activo", size=12, color=SUCCESS),
                            ], spacing=4),
                        ], vertical_alignment="center"),
                        ft.Container(height=24),
                        ft.Divider(color=BORDER, height=1),
                        ft.Container(height=16),
                        ft.Text("Cambiar contraseña", size=14, weight="bold", color=TEXT),
                        ft.Container(height=12),
                        pwd, pwd2, msg,
                        ft.Container(height=8),
                        btn_primary("Actualizar contraseña", cambiar, width=430),
                    ], spacing=12),
                ),
            ], spacing=4),
        ))

    # ─── LOGIN ───────────────────────────────────────────────────────────────

    def pantalla_login(self, e=None):
        self._reset_bg()
        self._rebuild_sidebar("login")
        usr = campo("Usuario")
        pwd = campo("Contraseña", password=True)
        msg = ft.Text("", color=DANGER, size=12)

        def entrar(e):
            err = _validar_usuario(usr.value.strip())
            if err:
                msg.value = err; self.page.update(); return
            if not pwd.value:
                msg.value = "Ingresa tu contraseña"; self.page.update(); return
            if db.login_usuario(usr.value.strip(), pwd.value):
                self.usuario = usr.value.strip()
                self._rebuild_sidebar()
                self.pantalla_inicio()
            else:
                msg.value = "Usuario o contraseña incorrectos"
                self.page.update()

        self._set(ft.Container(
            padding=48,
            content=ft.Column([
                section_label("Acceso al sistema"),
                ft.Container(height=6),
                titulo("Iniciar sesión", 28),
                subtitulo("Accede a tu cuenta de SofaLab 3D"),
                ft.Container(height=28),
                ft.Container(
                    bgcolor=SURFACE, border_radius=12,
                    border=borde(), padding=32, width=460,
                    content=ft.Column([
                        usr, pwd, msg,
                        ft.Container(height=4),
                        btn_primary("Ingresar", entrar, width=396),
                        ft.Container(height=8),
                        ft.Row([
                            btn_ghost("Crear cuenta", self.pantalla_registro),
                            btn_ghost("Olvidé mi contraseña", self.pantalla_recuperar),
                        ], alignment="spaceBetween"),
                    ], spacing=12),
                ),
            ], spacing=4),
        ))

    # ─── REGISTRO ────────────────────────────────────────────────────────────

    def pantalla_registro(self, e=None):
        self._reset_bg()
        usr  = campo("Usuario")
        pwd  = campo("Contraseña", password=True)
        pwd2 = campo("Confirmar contraseña", password=True)
        msg  = ft.Text("", size=12)

        def crear(e):
            err = _validar_usuario(usr.value.strip())
            if err:
                msg.value, msg.color = err, DANGER; self.page.update(); return
            err = _validar_pwd(pwd.value)
            if err:
                msg.value, msg.color = err, DANGER; self.page.update(); return
            if pwd.value != pwd2.value:
                msg.value, msg.color = "Las contraseñas no coinciden", DANGER
                self.page.update(); return
            if db.registrar_usuario(usr.value.strip(), pwd.value):
                msg.value, msg.color = "¡Cuenta creada! Ahora puedes iniciar sesión.", SUCCESS
            else:
                msg.value, msg.color = "Ese usuario ya existe", DANGER
            self.page.update()

        self._set(ft.Container(
            padding=48,
            content=ft.Column([
                section_label("Nueva cuenta"),
                ft.Container(height=6),
                titulo("Crear cuenta", 28),
                subtitulo("Únete a SofaLab 3D"),
                ft.Container(height=28),
                ft.Container(
                    bgcolor=SURFACE, border_radius=12,
                    border=borde(), padding=32, width=460,
                    content=ft.Column([
                        usr, pwd, pwd2, msg,
                        ft.Container(height=4),
                        btn_primary("Registrarse", crear, width=396),
                        ft.Container(height=8),
                        btn_ghost("← Volver al login", self.pantalla_login),
                    ], spacing=12),
                ),
            ], spacing=4),
        ))

    # ─── RECUPERAR ───────────────────────────────────────────────────────────

    def pantalla_recuperar(self, e=None):
        self._reset_bg()
        usr = campo("Usuario")
        pwd = campo("Nueva contraseña", password=True)
        msg = ft.Text("", size=12)

        def cambiar(e):
            err = _validar_usuario(usr.value.strip())
            if err:
                msg.value, msg.color = err, DANGER; self.page.update(); return
            err = _validar_pwd(pwd.value)
            if err:
                msg.value, msg.color = err, DANGER; self.page.update(); return
            if db.actualizar_password(usr.value.strip(), pwd.value):
                msg.value, msg.color = "Contraseña actualizada", SUCCESS
            else:
                msg.value, msg.color = "Usuario no encontrado", DANGER
            self.page.update()

        self._set(ft.Container(
            padding=48,
            content=ft.Column([
                section_label("Recuperar acceso"),
                ft.Container(height=6),
                titulo("Recuperar contraseña", 28),
                subtitulo("Define una nueva contraseña para tu cuenta"),
                ft.Container(height=28),
                ft.Container(
                    bgcolor=SURFACE, border_radius=12,
                    border=borde(), padding=32, width=460,
                    content=ft.Column([
                        usr, pwd, msg,
                        ft.Container(height=4),
                        btn_primary("Actualizar contraseña", cambiar, width=396),
                        ft.Container(height=8),
                        btn_ghost("← Volver al login", self.pantalla_login),
                    ], spacing=12),
                ),
            ], spacing=4),
        ))

    # ─── TELAS ───────────────────────────────────────────────────────────────

    def pantalla_telas(self):
        self._reset_bg()
        if not self.usuario:
            self.pantalla_login(); return
        self._rebuild_sidebar("telas")
        self._render_telas()

    def _render_telas(self):
        catalogos = db.listar_catalogos()
        secciones = []

        for cat in catalogos:
            telas = db.listar_telas(cat["id"])
            grid  = [self._card_tela(t) for t in telas]
            grid.append(self._card_agregar(cat["id"]))
            n_telas = len(telas)

            secciones.append(ft.Container(
                bgcolor=SURFACE, border_radius=12,
                padding=20, border=borde(),
                content=ft.Column([
                    ft.Row([
                        ft.Text(cat["nombre"], size=18, weight="bold", color=ACCENT),
                        ft.Container(
                            bgcolor=SURFACE2, border_radius=10,
                            padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                            content=ft.Text(
                                f"{n_telas} tela{'s' if n_telas != 1 else ''}",
                                size=11, color=TEXT_SUB,
                            ),
                        ),
                        ft.Container(expand=True),
                        ft.TextButton(
                            "✏️ Renombrar",
                            on_click=lambda e, cid=cat["id"], cn=cat["nombre"]:
                                self._dialogo_renombrar_catalogo(cid, cn),
                            style=ft.ButtonStyle(color=TEXT_SUB),
                        ),
                        ft.TextButton(
                            "Eliminar",
                            on_click=lambda e, cid=cat["id"], cn=cat["nombre"]:
                                self._confirmar_eliminar_catalogo(cid, cn),
                            style=ft.ButtonStyle(color=DANGER),
                        ),
                    ], spacing=8),
                    ft.Container(height=14),
                    ft.Row(grid, wrap=True, spacing=14),
                ]),
            ))

        nuevo_nombre = campo("Nombre del nuevo catálogo", expand=True)

        def crear_cat(e):
            n = nuevo_nombre.value.strip()
            if not n:
                snack(self.page, "Escribe un nombre", ok=False); return
            if db.crear_catalogo(n):
                nuevo_nombre.value = ""
                snack(self.page, f'Catálogo "{n}" creado')
                self._render_telas()
            else:
                snack(self.page, "Ya existe ese catálogo", ok=False)

        panel_nuevo = ft.Container(
            bgcolor=SURFACE, border_radius=12, padding=20, border=borde(),
            content=ft.Row([
                ft.Text("＋ Nuevo catálogo", size=14, weight="bold", color=TEXT),
                ft.Container(width=16),
                ft.Container(nuevo_nombre, expand=True),
                ft.Container(width=12),
                btn_primary("Crear", crear_cat),
            ]),
        )

        self._set(ft.Container(
            padding=48,
            content=ft.Column([
                section_label("Módulos del sistema"),
                ft.Container(height=6),
                titulo("Biblioteca de Materiales", 28),
                subtitulo("Catálogos de telas para tapicería"),
                divider(),
                ft.Container(height=8),
                panel_nuevo,
                ft.Container(height=8),
                *secciones,
                ft.Container(height=20),
            ], spacing=12, scroll="auto"),
        ))

    def _card_tela(self, tela: dict):
        tiene_img = os.path.isfile(tela["ruta_img"])
        img_widget = (
            ft.Image(src=tela["ruta_img"], width=160, height=160,
                     fit="cover", border_radius=8)
            if tiene_img else
            ft.Container(
                width=160, height=160, bgcolor=SURFACE2, border_radius=8,
                content=ft.Column([
                    ft.Text("🖼️", size=28),
                    ft.Text("Sin imagen", size=10, color=TEXT_SUB),
                ], alignment="center", horizontal_alignment="center"),
            )
        )
        return ft.Container(
            width=160, bgcolor=CARD_BG, border_radius=10,
            border=borde(), padding=8,
            content=ft.Column([
                img_widget,
                ft.Container(height=6),
                ft.Text(tela["nombre"], size=13, weight="bold", color=TEXT,
                        max_lines=1, overflow="ellipsis"),
                ft.Container(height=2),
                ft.TextButton(
                    "✕ Quitar",
                    on_click=lambda e, tid=tela["id"]: self._eliminar_tela(tid),
                    style=ft.ButtonStyle(color=DANGER),
                ),
            ], spacing=0),
        )

    def _card_agregar(self, catalogo_id: int):
        return ft.Container(
            width=160, height=210,
            bgcolor=SURFACE2, border_radius=10,
            border=borde(ACCENT2),
            on_click=lambda e: self._dialogo_agregar_tela(catalogo_id), ink=True,
            content=ft.Column([
                ft.Text("+", size=36, color=ACCENT),
                ft.Text("Agregar tela", size=12, color=TEXT_SUB),
            ], alignment="center", horizontal_alignment="center", spacing=6),
        )

    def _dialogo_agregar_tela(self, catalogo_id: int):
        nombre_f = campo("Nombre de la tela")
        ruta_f   = campo("Ruta de la imagen", hint="ej: telas/bordeaux.png")
        ayuda    = ft.Text("Extensiones válidas: png, jpg, jpeg, webp", size=10, color=TEXT_SUB)
        msg      = ft.Text("", size=11, color=DANGER)
        EXTS     = {".png", ".jpg", ".jpeg", ".webp"}

        def confirmar(e):
            n = nombre_f.value.strip()
            r = ruta_f.value.strip()
            if not n:
                msg.value = "Escribe un nombre para la tela"; self.page.update(); return
            if not r:
                msg.value = "Ingresa la ruta de la imagen"; self.page.update(); return
            if os.path.splitext(r)[1].lower() not in EXTS:
                msg.value = "Extensión no válida: usa png, jpg, jpeg o webp"; self.page.update(); return
            if not os.path.isfile(r):
                msg.value = "No se encontró el archivo en esa ruta"; self.page.update(); return
            if db.agregar_tela(catalogo_id, n, r):
                self.page.dialog.open = False; self.page.update()
                snack(self.page, f'"{n}" agregada al catálogo')
                self._render_telas()
            else:
                msg.value = "Error al agregar"; self.page.update()

        def cancelar(e):
            self.page.dialog.open = False; self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Agregar tela al catálogo", color=TEXT, weight="bold"),
            bgcolor=SURFACE,
            content=ft.Column([nombre_f, ruta_f, ayuda, msg], spacing=12, tight=True),
            actions=[btn_ghost("Cancelar", cancelar), btn_primary("Agregar", confirmar)],
            shape=ft.RoundedRectangleBorder(radius=12),
        )
        self.page.dialog = dlg; dlg.open = True; self.page.update()

    def _eliminar_tela(self, tela_id: int):
        db.eliminar_tela(tela_id)
        snack(self.page, "Tela eliminada del catálogo")
        self._render_telas()

    def _dialogo_renombrar_catalogo(self, catalogo_id: int, nombre_actual: str):
        nuevo_f = campo("Nuevo nombre")
        nuevo_f.value = nombre_actual
        msg = ft.Text("", size=11, color=DANGER)

        def confirmar(e):
            n = nuevo_f.value.strip()
            if not n:
                msg.value = "Escribe un nombre"; self.page.update(); return
            if db.renombrar_catalogo(catalogo_id, n):
                self.page.dialog.open = False; self.page.update()
                snack(self.page, f'Catálogo renombrado a "{n}"')
                self._render_telas()
            else:
                msg.value = "Ya existe un catálogo con ese nombre"; self.page.update()

        def cancelar(e):
            self.page.dialog.open = False; self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f'Renombrar "{nombre_actual}"', color=TEXT, weight="bold"),
            bgcolor=SURFACE,
            content=ft.Column([nuevo_f, msg], spacing=12, tight=True),
            actions=[btn_ghost("Cancelar", cancelar), btn_primary("Guardar", confirmar)],
            shape=ft.RoundedRectangleBorder(radius=12),
        )
        self.page.dialog = dlg; dlg.open = True; self.page.update()

    def _confirmar_eliminar_catalogo(self, catalogo_id: int, nombre: str):
        def confirmar(e):
            self.page.dialog.open = False; self.page.update()
            db.eliminar_catalogo(catalogo_id)
            snack(self.page, f'Catálogo "{nombre}" eliminado')
            self._render_telas()

        def cancelar(e):
            self.page.dialog.open = False; self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f'¿Eliminar "{nombre}"?', color=TEXT, weight="bold"),
            bgcolor=SURFACE,
            content=ft.Text(
                "Se eliminarán todas las telas. Esta acción no se puede deshacer.",
                color=TEXT_SUB,
            ),
            actions=[btn_ghost("Cancelar", cancelar), btn_danger("Eliminar", confirmar)],
            shape=ft.RoundedRectangleBorder(radius=12),
        )
        self.page.dialog = dlg; dlg.open = True; self.page.update()

    # ─── 3D ──────────────────────────────────────────────────────────────────

    def pantalla_3d(self):
        self._reset_bg()
        if not self.usuario:
            self.pantalla_login(); return
        self._rebuild_sidebar("3d")

        modelos = []
        if os.path.exists(RUTA_MODELOS):
            modelos = [
                f for f in os.listdir(RUTA_MODELOS)
                if f.endswith((".glb", ".egg", ".bam", ".gltf"))
            ]

        if not modelos:
            cuerpo = ft.Column([
                ft.Container(height=50),
                ft.Text("📦", size=52),
                ft.Text("No hay modelos disponibles", size=18, color=TEXT_SUB),
                subtitulo(f'Agrega archivos .glb en la carpeta "{RUTA_MODELOS}/"'),
            ], horizontal_alignment="center", spacing=10)
        else:
            cuerpo = ft.Row(
                [self._card_modelo(m) for m in modelos],
                wrap=True, spacing=16,
            )

        self._set(ft.Container(
            padding=48,
            content=ft.Column([
                section_label("Módulos del sistema"),
                ft.Container(height=6),
                titulo("Visualización 3D", 28),
                subtitulo("Selecciona un modelo para explorar"),
                divider(),
                ft.Container(height=18),
                cuerpo,
            ], spacing=8),
        ))

    def _card_modelo(self, archivo: str):
        return ft.Container(
            width=200, height=165,
            bgcolor=SURFACE, border_radius=12,
            padding=20, border=borde(),
            content=ft.Column([
                ft.Text("📦", size=38),
                ft.Text(archivo, size=13, color=TEXT, weight="bold",
                        max_lines=2, overflow="ellipsis"),
                ft.Container(expand=True),
                btn_primary("Abrir", lambda e, m=archivo: self._abrir_modelo(m)),
            ], spacing=8),
        )

    def _abrir_modelo(self, modelo: str):
        ruta = os.path.join(RUTA_MODELOS, modelo)
        if not os.path.isfile(ruta):
            snack(self.page, f"Archivo no encontrado: {modelo}", ok=False); return
        snack(self.page, f"Abriendo {modelo}…")
        subprocess.Popen([sys.executable, "main.py", modelo])


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main(page: ft.Page):
    App(page)


if __name__ == "__main__":
    ft.app(target=main)