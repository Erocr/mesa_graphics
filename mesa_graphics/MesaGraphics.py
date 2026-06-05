from mesa_graphics.View import View
from mesa_graphics.Controller import Controller
from mesa_graphics.Model import Model


class MesaGraphics:
    def __init__(self, model, components=None, name=None):
        self.model = Model(model)
        self.view = View(self.model, components=components, name=name)
        self.controller = Controller(self.model, self.view)
        self.loop()

    def loop(self):
        while not self.controller.is_terminated:
            self.controller.update()
            self.model.update()
            self.view.draw()
