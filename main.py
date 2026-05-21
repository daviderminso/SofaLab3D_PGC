import sys
from math import sin, cos, radians          # ← movido al tope, fuera del método

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, Vec4
from direct.task import Task

DIST_MIN  = 3
DIST_MAX  = 30
ANGULO_V_MIN = -10
ANGULO_V_MAX =  80
ZOOM_PASO    =  1.0
ROT_SPEED    = 150.0


class VisorModelo(ShowBase):
    """Visor 3D interactivo para modelos Panda3D (.glb / .egg / .bam / .gltf)."""

    def __init__(self, modelo: str):
        super().__init__()

        self.setBackgroundColor(0.1, 0.1, 0.1)

        # ── Nodo raíz del modelo ──────────────────────────────────────────────
        self.nodo = self.render.attachNewNode("nodo")
        self.modelo = self.loader.loadModel(f"modelos/{modelo}")
        self.modelo.reparentTo(self.nodo)
        self.modelo.setScale(1)
        self.modelo.setPos(0, 0, 0)

        # ── Cámara ───────────────────────────────────────────────────────────
        self.disableMouse()
        self.distancia = 10.0
        self.angulo_h  = 0.0
        self.angulo_v  = 10.0
        self._actualizar_camara()

        # ── Iluminación ──────────────────────────────────────────────────────
        ambient = AmbientLight("ambient")
        ambient.setColor(Vec4(0.7, 0.7, 0.7, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        directional = DirectionalLight("dir")
        directional.setColor(Vec4(1, 1, 1, 1))
        directional.setDirection((1, -1, -1))
        self.render.setLight(self.render.attachNewNode(directional))

        # ── Estado del ratón ─────────────────────────────────────────────────
        self._rotando = False
        self._last_x  = 0.0
        self._last_y  = 0.0

        # ── Eventos ──────────────────────────────────────────────────────────
        self.accept("mouse1",    self._iniciar_rotacion)
        self.accept("mouse1-up", self._detener_rotacion)
        self.accept("wheel_up",  self._zoom_in)
        self.accept("wheel_down",self._zoom_out)
        self.accept("escape",    sys.exit)          # salir con Escape

        self.taskMgr.add(self._update, "update")

    # ── Rotación ─────────────────────────────────────────────────────────────

    def _iniciar_rotacion(self) -> None:
        self._rotando = True
        if self.mouseWatcherNode.hasMouse():
            self._last_x = self.mouseWatcherNode.getMouseX()
            self._last_y = self.mouseWatcherNode.getMouseY()

    def _detener_rotacion(self) -> None:
        self._rotando = False

    # ── Zoom ─────────────────────────────────────────────────────────────────

    def _zoom_in(self) -> None:
        self.distancia = max(DIST_MIN, self.distancia - ZOOM_PASO)
        self._actualizar_camara()

    def _zoom_out(self) -> None:
        self.distancia = min(DIST_MAX, self.distancia + ZOOM_PASO)
        self._actualizar_camara()

    # ── Cámara esférica ──────────────────────────────────────────────────────

    def _actualizar_camara(self) -> None:
        h = radians(self.angulo_h)
        v = radians(self.angulo_v)

        x = self.distancia * sin(h) * cos(v)
        y = -self.distancia * cos(h) * cos(v)
        z = self.distancia * sin(v)

        self.camera.setPos(x, y, z)
        self.camera.lookAt(self.nodo)

    # ── Loop principal ───────────────────────────────────────────────────────

    def _update(self, task) -> int:
        if self._rotando and self.mouseWatcherNode.hasMouse():
            x = self.mouseWatcherNode.getMouseX()
            y = self.mouseWatcherNode.getMouseY()

            self.angulo_h -= (x - self._last_x) * ROT_SPEED
            self.angulo_v  = max(
                ANGULO_V_MIN,
                min(ANGULO_V_MAX, self.angulo_v + (y - self._last_y) * ROT_SPEED),
            )

            self._actualizar_camara()

            self._last_x = x
            self._last_y = y

        return Task.cont


# ─── ENTRADA ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py <nombre_modelo>")
        sys.exit(1)

    visor = VisorModelo(sys.argv[1])
    visor.run()