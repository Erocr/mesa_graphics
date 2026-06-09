from mesa_graphics.View import View
from mesa_graphics.Controller import Controller
from mesa_graphics.Model import Model
from time import time


class MesaGraphics:
    def __init__(self, model, renderer=None, components=None, model_params=None, name=None):
        self.model = Model(model)
        self.view = View(self.model, renderer=renderer, components=components, model_params=model_params, name=name)
        self.controller = Controller(self.model, self.view)
        self.start()

    def start(self):
        while not self.controller.is_terminated:
            start = time()
            self.controller.update()
            self.model.update()
            self.view.draw()
            self.model.debug_infos["fps"] = 1/(time() - start)
