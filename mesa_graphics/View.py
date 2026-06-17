from typing import Callable

from mesa_graphics.Component import Component
from mesa_graphics.UIElement import *
from mesa_graphics.matplotlib_components import create_space_component
from time import time
import mesa.visualization.user_param as mesa_user_param


class View:
    SCROLL_SENSIBILITY = 10

    def __init__(self, model, renderer=None, components=None, play_interval=100, render_interval=1, model_params=None,
                 name=None):
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
        self.max_page_scrolling_y = 0
        self.page_scrolling_y = 0
        self.page = 0
        self.min_page = self.max_page = 0
        self.min_visible_page = 0
        if components is None:
            self.components = {0: []}
        else:
            self.components = {0: []}
            self._store_components(components)
        if renderer is not None:
            self.components[0].insert(0, Component(self.model, create_space_component(renderer)))
        self.buttons = {}  # Provide fast and easy access to buttons
        self.userTweakableModelParams = {}  # Provide fast and easy access to user parameters
        self.userEntries = {}
        self.ui_elements = []
        if name is None:
            name = type(self.model).__name__
        self._create_ui(name, model_params, play_interval, render_interval)

    def quit(self):
        """ End the visualization """
        pg.quit()

    def add_UIElement(self, typ: type, *args, **kwargs):
        """ This function instantiates a new UIElement.

        :param typ: The type of the object we want to create.
        :param args: The parameters to pass in the class that we want to instantiate.
        :param kwargs: The parameters to pass in the class that we want to instantiate.
        :return: the object instantiated

        For example, if you want to instantiate a Button, call add_UIElement(Button, ...).
        """
        to_add = typ(*args, **kwargs)
        self.ui_elements.append(to_add)
        if isinstance(to_add, Button):
            self.buttons[to_add.name] = to_add
        if isinstance(to_add, UserParam):
            if to_add.model_param:
                self.userTweakableModelParams[to_add.name] = to_add
            else:
                self.userEntries[to_add.name] = to_add
        return to_add

    def _store_components(self, components: list[tuple[Callable, int] | Callable]):
        """
        Store the components in a more suitable way, so it will be easier to access.
        It associates to each page the list of components that are in this page.

        :param components: a list of components. Each component can be a tuple (component, page), or only a component.

        For each element of components. If it is only a component, it will be by default placed at the page 0.
        Moreover, if not all th pages are used, it will create empty pages automatically. For example, if you have
        page 0 and 3 used, it will create automatically pages 1 and 2 blank.
        """
        for comp_page in components:
            if isinstance(comp_page, tuple):
                comp, page = comp_page
            else:
                comp, page = comp_page, 0
            if page not in self.components:
                self.components[page] = []
            self.components[page].append(Component(self.model, comp))
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

    def _create_ui(self, name: str, model_params, play_interval: int, render_interval: int) -> None:
        """ Instantiate the UI. """
        self._create_up_bar(name)
        self._create_switch_page_buttons()
        self._create_controls(model_params, play_interval, render_interval)

    def _create_up_bar(self, name: str) -> None:
        """ Creates the blue bar on top of the screen, and write the name into it. """
        self.add_UIElement(Rectangle, pg.Vector2(0, 0), pg.Vector2(1280, 80), (0, 80, 255))
        text = self.add_UIElement(Text, pg.Vector2(80, 0), name)
        text.set_pos(text.pos + pg.Vector2(0, 40 - text.image.get_height()/2))

    def _create_controls(self, model_params, play_interval: int, render_interval: int) -> None:
        """
        This function creates the grey column in the left part of the screen, and fills it with the user parameters.
        It creates also the 3 buttons RESET, START/STOP, and STEP
        """
        self.add_UIElement(Rectangle, pg.Vector2(0, 80), pg.Vector2(300, 660), (220, 220, 220))
        x = 1050
        texts = ("RESET", "START", "STEP")
        names = ("RESET", "START/STOP", "STEP")

        for i in range(3):
            button = self.add_UIElement(Button, pg.Vector2(x, 22), texts[i], font_size=15, name=names[i])
            x += button.text.image.get_width() + 30
        self._create_flow_control_entries(play_interval, render_interval)
        if model_params is not None:
            self._create_model_params_entries(model_params)

    def _create_switch_page_buttons(self) -> None:
        """
        This function creates the buttons on top of the screen which allow to change the page.
        They are aligned.
        If there are too many pages, it shows buttons that allow to change the page-switching buttons shown.
        """
        buttons = []
        for i in range(self.min_page, self.max_page+1):
            buttons.append(self.add_UIElement(Button, pg.Vector2(0, 0), f"PAGE {i}", font_size=15))
        size_x = sum([button.size.x for button in buttons]) + 10 * (len(buttons) - 1)
        x = (1280 + 300) // 2 - size_x // 2
        for button in buttons:
            button.set_pos(pg.Vector2(x, 90))
            x += button.size.x + 10

        page_left = self.add_UIElement(Button, pg.Vector2(0, 0), "<", font_size=15, name="PAGE LEFT")
        page_right = self.add_UIElement(Button, pg.Vector2(0, 0), ">", font_size=15, name="PAGE RIGHT")
        page_right.visible = False
        page_left.visible = False
        page_right.lock()
        page_left.lock()

        if self.max_page+1 - self.min_page > 9:
            min_visible_page = min(max(self.min_page, -4), self.max_page-8)
            self.set_min_visible_page(min_visible_page)
        self.buttons[f"PAGE {self.page}"].lock()

    def page_right(self) -> None:
        """
        The action called when the user click on the PAGE RIGHT button (<)
        Change the interval of page-switching buttons you can see.
        """
        self.set_min_visible_page(min(self.max_page - 8, self.min_visible_page + 6))

    def page_left(self) -> None:
        """
        The action called when the user click on the PAGE LEFT button (<)
        Change the interval of page-switching buttons you can see.
        """
        self.set_min_visible_page(max(self.min_page, self.min_visible_page - 6))

    def set_min_visible_page(self, min_visible_page: int) -> None:
        """
        When you have too much pages, the interface will show only 8 page-switching buttons.
        The pages chosen are from min_visible_page to min_visible_page+8.
        So the function set the attribute min_visible_page with the one chosen, and then rearrange the buttons, so
        that we see this buttons at the right places.
        """
        self.min_visible_page = min_visible_page
        for button in self.buttons.values():
            if button.name[:4] == "PAGE":
                button.visible = False
                button.lock()
        visible_buttons = [self.buttons["PAGE LEFT"]] + \
                          [self.buttons[f"PAGE {i}"] for i in range(self.min_visible_page, self.min_visible_page+9)] + \
                          [self.buttons["PAGE RIGHT"]]
        size_x = sum([button.size.x for button in visible_buttons]) + 10 * (len(visible_buttons) - 1)
        x = (1280 + 300) // 2 - size_x // 2
        for button in visible_buttons:
            button.set_pos(pg.Vector2(x, 90))
            x += button.size.x + 10
            button.visible = True
            button.unlock()
        self.buttons[f"PAGE {self.page}"].lock()

    def _create_flow_control_entries(self, play_interval: int, render_interval: int) -> None:
        """
        Create the flow control user parameters. Thus are the two sliders "play interval" and "render interval".
        :param play_interval: The starting value of the play_interval's slider
        :param render_interval: The starting value of the render_interval's slider
        """
        y = 90
        play_interval_params = {
            "type": "SliderInt",
            "min": 0,
            "max": 2000,
            "step": 10,
            "value": play_interval,
            "param_name": "play_interval",
            "label": "play interval (ms):",
            "model_param": False
        }
        y = self._create_user_param("play_interval", play_interval_params, y)

        render_interval_params = {
            "type": "SliderInt",
            "min": 1,
            "max": 50,
            "step": 1,
            "value": render_interval,
            "param_name": "render_interval",
            "label": "render interval (steps): ",
            "model_param": False
        }
        self._create_user_param("render_interval", render_interval_params, y)

    def _create_model_params_entries(self, model_params) -> None:
        """
        Create the tweakable user parameters in the left column, which describe how to re-instantiate the model using
        the RESET button.
        """
        y = 300
        for param_name in model_params:
            y = self._create_user_param(param_name, model_params[param_name], y)

    def _create_user_param(self, param_name: str, model_param, y: int) -> int:
        """
        Create a user parameter (UserParam). A user parameter is something that the user can tweak.
        :param param_name: The name of the user parameter. It is used as an ID to recognize the user parameter.
        If this name already exists, we will automatically add numbers at the end of the name.
        :param model_param: a boolean, set to true if the value of the user parameter is uses as a parameter for the
        next instantiation of the user's model.
        :param y: The vertical position at which the user parameter widget should be placed.
        :return: The next available vertical position. This value can be used to place subsequent UI elements without
        overlapping this widget.
        """
        p = self._user_input_params_extraction(model_param, param_name)
        if p is not None:
            type, param = p
            label = param_name
            if "label" in param:
                label = param.pop("label")

            x, y, lastUiElement = self._add_model_param_label(label, y)
            x = 10
            y += lastUiElement.image.get_height()
            args = self._compute_args_for_user_params_creation(type, x, y)
            self.add_UIElement(type, *args, **param)

        return y + 30

    def _user_input_params_extraction(self, param, param_name: str) -> tuple[type[UserParam], dict]:
        """
        The user can describe a param with a dictionary, but can also describe it with a mesa_user_param.Slider.

        This functions see how the user describes his userParam, and transform this description in a dictionary
        description.

        :return: Tuple (UIElementClass, parameter_dict) if the parameter definition is recognized, raise an error.
        """
        if isinstance(param, dict):
            param["param_name"] = param_name
            t = param.pop("type")
            param["t"] = t
            if t in ("SliderInt", "SliderFloat"):
                return Slider, param
            elif t == "Checkbox":
                return Checkbox, param
            raise NotImplementedError(f"The type {t} has not been implemented")
        elif isinstance(param, mesa_user_param.Slider):
            res = {
                "param_name": param_name,
                "label": param.label,
                "min": param.min,
                "max": param.max,
                "step": param.step,
                "value": param.value,
                "t": ("SliderInt", "SliderFloat")[param.is_float_slider]
            }
            return Slider, res

    def _compute_args_for_user_params_creation(self, t: type[UserParam], x: int, y: int):
        """
        Build the positional arguments required to instantiate a specific UserParam widget.
        :param t: Widget class to instantiate.
        :return: Tuple of positional arguments compatible with add_UIElement().
        """
        if t == Slider:
            return pg.Vector2(x, y), 290 - x
        elif t == Checkbox:
            return (pg.Vector2(x, y-Checkbox.SIZE.y/2),)

    def _add_model_param_label(self, label: str, y: int) -> tuple[int | float, int | float, Text]:
        """
        Helper function that creates the label as Text for a model parameter.

        :return: (next_x, center_y, text_element)
        """
        labels = self._split_label(label)
        if len(labels) == 0: labels = [label]
        text = None
        for label in labels:
            if text is not None: y += text.image.get_height()
            text = self.add_UIElement(Text, pg.Vector2(10, y), label, font_size=20)
        return text.image.get_width() + 20, y+text.image.get_height()/2, text  # noqa

    def _split_label(self, label: str):
        """ Split the labels so that only max_number_chars characters are in any line. """
        max_number_chars = 24
        res = []
        words = label.split(" ")
        i = -1
        last_chosen_i = 0
        current_size = 0
        while i+1 < len(words):
            i += 1
            current_size += len(words[i]) + 1
            if current_size > max_number_chars:
                if i > last_chosen_i:
                    r = ""
                    for j in range(last_chosen_i, i):
                        r += words[j] + " "
                    res.append(r[:-1])
                    last_chosen_i = i
                    i -= 1
                else:
                    while len(words[i]) >= max_number_chars:
                        res.append(words[i][:max_number_chars])
                        words[i] = words[i][max_number_chars:]
                    current_size = len(words[i])
                    last_chosen_i = i
        r = ""
        for j in range(last_chosen_i, i+1):
            r += words[j] + " "
        res.append(r[:-1])
        return res

    def render(self):
        """
        Renders all the component images according to the model state. It stores the images in the components
        themselves. Note that these operations are really heavy.
        """
        for component in self.components[self.page]:
            component.render()

    def draw(self):
        """
        Main function. It is called once per frame. It refreshes the screen and draws all the information in it.
        """
        start = time()
        self.screen.fill((255, 255, 255))
        self.draw_components()
        self._page_scroll_clamp()
        for ui in self.ui_elements:
            ui.draw(self.screen)
        if self.model.debug: self.draw_debug()
        self.model.debug_infos["viewer_time"] = time() - start
        pg.display.flip()

    def draw_components(self):
        """
        This function draws all the components in the current page.
        """
        y = 135 - self.page_scrolling_y
        next_y = y - 55
        x = 300
        for component in self.components[self.page]:
            image = component.image
            if image is None:
                continue
            size = image.get_size()
            if size[0] + x > 1280:
                y = next_y + 10
                next_y = y
                x = 300
            next_y = max(next_y, y + size[1])
            self.screen.blit(image, (x, y))
            x += size[0] + 10
        self.max_page_scrolling_y = max(next_y - 700 + self.page_scrolling_y, 0)

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

    def switch_page(self, new_page: int):
        """
        Switch to another page and update page-selection buttons.

        Resets the page scrolling position.
        """
        self.buttons[f"PAGE {self.page}"].unlock()
        self.page = new_page
        self.buttons[f"PAGE {self.page}"].lock()
        self.page_scrolling_y = 0

    def scroll(self, amount: int):
        """
        Scroll through the components if there are to many components.
        :param amount: how much the user is scrolling.
        """
        self.page_scrolling_y += amount * self.SCROLL_SENSIBILITY
        self._page_scroll_clamp()

    def _page_scroll_clamp(self):
        """ Clamp the scroll value if it is too high or too low. """
        if self.page_scrolling_y <= 0:
            self.page_scrolling_y = 0
        elif self.page_scrolling_y >= self.max_page_scrolling_y:
            self.page_scrolling_y = self.max_page_scrolling_y

