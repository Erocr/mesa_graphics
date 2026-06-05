from mesa_graphics.View import View
from mesa_graphics.Controller import Controller


class MesaGraphics:
    def __init__(self, model, components=None, name=None):
        self.view = View(model, components=components, name=name)
        self.controller = Controller(model, self.view)
        self.loop()

    def loop(self):
        while not self.controller.is_terminated:
            self.controller.update()
            self.view.draw()
