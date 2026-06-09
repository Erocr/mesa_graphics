from mesa_graphics.UIElement import *
from mesa_graphics.matplotlib_components import create_space_component
from time import time


class View:
    def __init__(self, model, renderer=None, components=None, model_params=None, name=None):
        """ View class.
        /!\\ The user must not use this class, use MesaGraphics instead /!\\

        This class provides all the logic for the graphics. It handles the screen and draws on it.

        :param model: A Model instance that will be visualized. It is the MesaGraphic's Model, and not
        the user's on
        :param renderer: (SpaceRenderer) A SpaceRenderer instance to render the model's space.
        :param components: List of tuples (component, page).
        component is a function that take a model instance, and returns a pygame Surface representing it.
        You can create them with the matplotlib_components's utility functions, or you can create custom ones.
        The page is an integer, describing in which page it must be drawn.
        :param model_params: Parameters for re-instantiating a model.
            Can include user-adjustable parameters and fixed parameters. Defaults to None.
        :param name: Name of the visualization. Defaults to the model's class name.
        """
        pg.font.init()
        self.screen = pg.display.set_mode((1280, 740), pg.RESIZABLE)
        self.model = model
        self.page = 0
        self.min_page = self.max_page = 0
        if components is None:
            pass
        else:
            self.components = {0: []}
            self.components = {0: []}
            self._store_components(components)
        if renderer is not None:
            self.components[0].insert(0, create_space_component(renderer))
        self.buttons = {}  # Provide fast and easy access to buttons
        self.sliders = {}  # Provide fast and easy access to sliders
        self.ui_elements = []
        if name is None:
            name = type(self.model).__name__
        self._create_ui(name, model_params)

    def add_UIElement(self, type, *args, **kwargs):
        """ This function instantiates a new UIElement.

        :param type: The type of the object we want to create.
        :param args: The parameters to pass in the class that we want to instantiate.
        :param kwargs: The parameters to pass in the class that we want to instantiate.
        :return: the object instantiated

        For example, if you want to instantiate a Button, call add_UIElement(Button, ...).
        """
        to_add = type(*args, **kwargs)
        self.ui_elements.append(to_add)
        if isinstance(to_add, Button):
            self.buttons[to_add.name] = to_add
        return to_add

    def _store_components(self, components):
        """ Store the components in a more suitable way, so it will be easier to access. """
        for comp_page in components:
            comp, page = comp_page
            if page not in self.components:
                self.components[page] = []
            self.components[page].append(comp)
        self._add_unuseful_pages()

    def _add_unuseful_pages(self):
        """
        Create as many blank pages as needed.
        If the user put something in the 0-th page anf the second page, this function creates a blank
        page for page 1.
        """
        self.min_page = 0
        self.max_page = 0
        for page in self.components:
            if page < self.min_page: self.min_page = page
            if page > self.max_page: self.max_page = page
        for i in range(self.min_page+1, self.max_page):
            if i not in self.components:
                self.components[i] = []

    def _create_ui(self, name, model_params):
        """ Instantiate the UI. """
        self._create_up_bar(name)
        self._create_switch_page_buttons()
        self._create_controls(model_params)


    def _create_up_bar(self, name):
        """ Creates the blue bar on top of the screen, and write the name into it. """
        self.add_UIElement(Rectangle, pg.Vector2(0, 0), pg.Vector2(1280, 80), (0, 80, 255))
        self.add_UIElement(Text, pg.Vector2(80, 0), name)

    def _create_controls(self, model_params):
        """
        This function creates the grey column in the left part of the screen, and fills it.
        It creates also the 3 buttons RESET, START/STOP, and STEP
        """
        self.add_UIElement(Rectangle, pg.Vector2(0, 80), pg.Vector2(300, 660), (220, 220, 220))
        x = 1050
        texts = ("RESET", "START", "STEP")
        names = ("RESET", "START/STOP", "STEP")

        for i in range(3):
            button = self.add_UIElement(Button, pg.Vector2(x, 22), texts[i], font_size=15, name=names[i])
            x += button.text.image.get_width() + 30
        if model_params is not None:
            self._create_model_params_entries(model_params)

    def _create_switch_page_buttons(self):
        """
        This function creates the buttons on top of the components part of the screen which
        allow to change the page. They are aligned
        """
        buttons = []
        for i in range(self.min_page, self.max_page+1):
            buttons.append(self.add_UIElement(Button, pg.Vector2(0, 0), f"PAGE {i}", font_size=15))
        size_x = sum([button.size.x for button in buttons]) + 10 * (len(buttons) - 1)
        x = (1280 + 300) // 2 - size_x // 2
        for button in buttons:
            button.set_pos(pg.Vector2(x, 90))
            x += button.size.x + 10

    def _create_model_params_entries(self, model_params):
        """
        Create the sliders in the left column, which describe how to re-instantiate the model using the
        RESET button
        ."""
        y = 90
        for param_name in model_params:
            param = model_params[param_name]
            label = param_name
            if "label" in param:
                label = param.pop("label")

            x, y, lastUiElement = self._add_model_param_label(label, y)
            if x > 250:
                x = 10
                y += lastUiElement.image.get_height()
            t = param.pop("type")
            slider = self.add_UIElement(Slider, t, pg.Vector2(x, y), 290 - x, **param)
            self.sliders[param_name] = slider
            y += 30

    def _add_model_param_label(self, label, y):
        """
        Helper function that creates the label for a model parameter.
        TODO: put it on multiple lines if label is to long
        """
        text = self.add_UIElement(Text, pg.Vector2(10, y), label, font_size=20)
        return text.image.get_width() + 20, y+text.image.get_height()/2, text

    def draw(self):
        """
        Main function. It is called once per frame. It refreshes the screen and draws all the information.
        """
        start = time()
        self.screen.fill((255, 255, 255))
        for ui in self.ui_elements:
            ui.draw(self.screen)
        self.draw_components()
        if self.model.debug: self.draw_debug()
        self.model.debug_infos["viewer_time"] = time() - start
        pg.display.flip()

    def draw_components(self):
        """
        This function draws all the components in the current page.
        TODO: compute the images only if it is necessary, don't re-compute them if the model doesn't change.
        """
        y = 135
        next_y = 80
        x = 300
        for component in self.components[self.page]:
            image = component(self.model.mesa_model)
            size = image.get_size()
            if size[0] + x > 1280:
                y = next_y + 10
                next_y = y
                x = 300
            next_y = max(next_y, y + size[1])
            self.screen.blit(image, (x, y))
            x += size[0] + 10

    def draw_debug(self):
        """
        This function draws debug information to help programmer, or maybe the user.
        This function is called only if you enter the debug mode by pressing "d".
        """
        texts = []
        for info in self.model.debug_infos:
            texts.append(info + ": " + str(self.model.debug_infos[info]))
        font = pg.font.Font('freesansbold.ttf', 15)
        y = 0
        for text in texts:
            image = font.render(text, False, (255, 255, 255), (0, 0, 0, 125))
            self.screen.blit(image, pg.Vector2(0, y))
            y += image.get_height()

