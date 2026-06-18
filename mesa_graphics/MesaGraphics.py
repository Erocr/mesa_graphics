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
        See the Mesa documentation for more information.

        :param model: A Model instance that will be visualized.
        :param renderer: (SpaceRenderer) A SpaceRenderer instance to render the model's space.
        :param components: List of tuples (component, page).
        component is a function that take a model instance, and returns a pygame Surface representing it.
        You can create them with the matplotlib_components's utility functions, or you can create custom ones.
        The page is an integer, describing in which page it must be drawn.
        :param model_params: Parameters for re-instantiating a model.
            Can include user-adjustable parameters and fixed parameters. Defaults to None.
        :param name: Name of the visualization. Defaults to the model's class name.
        """
        if simulator is not None: print("Warning: the simulator selected is not taken into account")
        if use_threads: print("Warning: the use_threads selected is not taken into account, this implementation always "
                              "use threads")

        self.model = Model(model, play_interval, render_interval)
        self.view = View(self.model, renderer=renderer, components=components, play_interval=play_interval,
                         render_interval=render_interval, model_params=model_params, name=name)
        self.controller = Controller(self.model, self.view)
        self.barrier = threading.Barrier(2)
        self.update_thread = threading.Thread(target=self._update_thread_loop)
        self.update_thread.start()
        self._view_thread_loop()

    def _view_thread_loop(self):
        """ Main loop executed in the main thread.

        Pygame APIs are not thread-safe and must only be called from the main thread.
        So this thread is responsible to:
        1. Take into account the user's inputs
        2. Draw onto the screen

        This thread must be as fast as possible in order to have a responsive graphical interface.
        So, execute all the heavy computations in the worker thread.
        """
        while not self.controller.is_terminated:
            self.controller.update()
            self.view.draw()
            sleep(0.001)
        self.view.quit()
        self.barrier.wait()

    def _update_thread_loop(self):
        """ Worker loop executed in the secondary thread.

        It must execute all the computationally expensive operations. It has the role to:
        1. update the model
        2. render (make the plots, and transform them in pygame.Surfaces)

        Update the model can be really long, it depends on the user's implementation.
        Rendering can also be very time-consuming, and user can create custom components, making it possibly even
        slower.
        """
        while not self.controller.is_terminated:
            start = time()
            self.model.update()
            self.view.render()
            d = time() - start
            if d < self.model.play_interval * 0.001:
                sleep(self.model.play_interval * 0.001 - d)
        self.barrier.wait()
