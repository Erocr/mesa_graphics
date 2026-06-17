from typing import Callable
from mesa_graphics.Model import Model


class Component:
    def __init__(self, model: Model, component_func: Callable):
        """
        Remembers the image associated to the component, so that the worker thread update this image, while the
        main thread draws it.

        :param model: The Model of MesaGraphics
        :param component_func: The function component-function. This function returns a pg.Surface.
        """
        self.model = model
        self.component_func = component_func
        self.image = None

    def render(self):
        self.image = self.component_func(self.model.mesa_model)
        if self.image is None:
            raise RuntimeError("The component didn't return anything. "
                               "Hint: maybe you forgot to to put the return keyword at the end of the function.")
