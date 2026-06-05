from mesa_graphics.View import View
from mesa_graphics.Controller import Controller


class MesaGraphics:
    def __init__(self):
        self.view = View()
        self.controller = Controller()
        self.loop()

    def loop(self):
        while not self.controller.is_terminated:
            self.controller.update()
            self.view.draw()
