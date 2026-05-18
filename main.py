import sys
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, Vec4
from direct.task import Task


class App(ShowBase):
    def __init__(self, modelo):
        super().__init__()

        self.setBackgroundColor(0.1, 0.1, 0.1)

        self.nodo = self.render.attachNewNode("nodo")

        self.modelo = self.loader.loadModel(f"modelos/{modelo}")
        self.modelo.reparentTo(self.nodo)
        self.modelo.setScale(1)
        self.modelo.setPos(0, 0, 0)

        self.disableMouse()
        self.distancia = 10
        self.angulo_h = 0
        self.angulo_v = 10

        self.actualizar_camara()

        ambient = AmbientLight("ambient")
        ambient.setColor(Vec4(0.7, 0.7, 0.7, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        directional = DirectionalLight("dir")
        directional.setColor(Vec4(1, 1, 1, 1))
        directional.setDirection((1, -1, -1))
        self.render.setLight(self.render.attachNewNode(directional))

        self.rotando = False
        self.last_x = 0
        self.last_y = 0

        self.accept("mouse1", self.iniciar_rotacion)
        self.accept("mouse1-up", self.detener_rotacion)

        self.accept("wheel_up", self.zoom_in)
        self.accept("wheel_down", self.zoom_out)

        self.taskMgr.add(self.update, "update")

    def iniciar_rotacion(self):
        self.rotando = True
        if self.mouseWatcherNode.hasMouse():
            self.last_x = self.mouseWatcherNode.getMouseX()
            self.last_y = self.mouseWatcherNode.getMouseY()

    def detener_rotacion(self):
        self.rotando = False

    def zoom_in(self):
        self.distancia -= 1
        if self.distancia < 3:
            self.distancia = 3
        self.actualizar_camara()

    def zoom_out(self):
        self.distancia += 1
        if self.distancia > 30:
            self.distancia = 30
        self.actualizar_camara()

    def actualizar_camara(self):
        from math import sin, cos, radians

        h = radians(self.angulo_h)
        v = radians(self.angulo_v)

        x = self.distancia * sin(h) * cos(v)
        y = -self.distancia * cos(h) * cos(v)
        z = self.distancia * sin(v)

        self.camera.setPos(x, y, z)
        self.camera.lookAt(self.nodo)

    def update(self, task):
        if self.rotando and self.mouseWatcherNode.hasMouse():
            x = self.mouseWatcherNode.getMouseX()
            y = self.mouseWatcherNode.getMouseY()

            dx = x - self.last_x
            dy = y - self.last_y

            self.angulo_h -= dx * 150
            self.angulo_v += dy * 150

            if self.angulo_v > 80:
                self.angulo_v = 80
            if self.angulo_v < -10:
                self.angulo_v = -10

            self.actualizar_camara()

            self.last_x = x
            self.last_y = y

        return Task.cont


if __name__ == "__main__":
    if len(sys.argv) > 1:
        modelo = sys.argv[1]
    else:
        sys.exit()

    app = App(modelo)
    app.run()