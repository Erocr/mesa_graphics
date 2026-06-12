from mesa_graphics.View import View
from mesa_graphics.Controller import Controller
from mesa_graphics.Model import Model
from time import time, sleep
import threading


class MesaGraphics:
    def __init__(self, model: Model,
                 renderer=None,
                 components=None,
                 play_interval: int = 100,
                 render_interval: int = 1,
                 simulator=None,
                 model_params=None,
                 name: str | None = None,
                 use_threads: bool = False):
        """Mesa Graphics component.

        This component provides a visualization interface for a given model using pygame.
        It supports various visualization components and allows for interactive model
        stepping and parameter adjustments. It is inspired by the SolaraViz function.
        Check the documentation of mesa to learn more about it.

        :param model: A Model instance that will be visualized. It must not be a reactive Model.
        :param renderer: (SpaceRenderer) A SpaceRenderer instance to render the model's space.
        :param components: List of tuples (component, page).
        component is a function that take a model instance, and returns a pygame Surface representing it.
        You can create them with the matplotlib_components's utility functions, or you can create custom ones.
        The page is an integer, describing in which page it must be drawn.
        :param model_params: Parameters for re-instantiating a model.
            Can include user-adjustable parameters and fixed parameters. Defaults to None.
        :param name: Name of the visualization. Defaults to the model's class name.
        """
        if play_interval != 100: print("Warning: the play_interval selected is not taken into account")
        if render_interval != 1: print("Warning: the render_interval selected is not taken into account")
        if simulator is not None: print("Warning: the simulator selected is not taken into account")
        if use_threads: print("Warning: the use_threads selected is not taken into account")

        self.model = Model(model, play_interval, render_interval)
        self.view = View(self.model, renderer=renderer, components=components, play_interval=play_interval,
                         render_interval=render_interval, model_params=model_params, name=name)
        self.controller = Controller(self.model, self.view)
        self.update_thread = threading.Thread(target=self._start_update)
        self.update_thread.start()
        self._start_view()

    def _start_view(self):
        """ This function start the visualization loop """
        while not self.controller.is_terminated:
            self.controller.update()
            self.view.draw()
            sleep(0.001)
        threading.Barrier(0)

    def _start_update(self):
        while not self.controller.is_terminated:
            start = time()
            self.model.update()
            self.view.render()
            d = time() - start
            if d < self.model.play_interval * 0.001:
                sleep(self.model.play_interval * 0.001 - d)
        threading.Barrier(0)
