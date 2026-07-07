import warnings

from .Component import Component
from .UIElement import *
from .components import create_space_component
import mesa.visualization.user_param as mesa_user_param

"""
This file contains the logic for drawing.
It is divided in three classes: 
View is the front class, and it is the one that handles all through the other classes.
UserParamView handles only the left column bar, and what is inside. 
ComponentsView handles the page system, and the components.



The important functions:
- View._create_ui  (called in View.__init__, describes where are placed each UIElement)
- ComponentsView.create_ui
- UserParamView.create_ui
- View.add_UIElement
- View.draw  (called once per frame)
- ComponentsView.draw  (called by View.draw)
"""


class View:
    SCROLL_SENSIBILITY = 15

    def __init__(self, model, renderer=None, components=None, play_interval=100, render_interval=1, model_params=None,
                 custom_method_call=None, name=None):
        """ View class.
        /!\\ The user must not use this class, use MesaGraphics instead /!\\

        This class provides all the logic for the graphics. It handles the screen and draws on it.
        The class is divided in two other classes, for a better subdivision. The UserParamView class handles the logic
        for drawing the control bar. The ComponentsView handles the drawing of components.

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
        self.fonts = {}
        self.init_fonts()
        self.screen_size = pg.Vector2(1280, 740)
        self.screen = pg.display.set_mode(self.screen_size, pg.RESIZABLE)
        self.model = model
        self.componentsView = ComponentsView(self, components, renderer)
        self.userParamView = UserParamView(self)
        self.ratio = pg.Vector2(1, 1)

        self.buttons = {}  # Provide fast and easy access to buttons
        self.ui_elements = []  # List of UI
        self.ui_focused = None  # UI element focused, the other are not interactive while one is focused
        # Only the sliders, and the Selects can be focused yet.

        if name is None:
            name = type(self.model).__name__
        self._create_ui(name, model_params, custom_method_call, play_interval, render_interval)

    def render(self):
        """
        Renders all the component images according to the model state. It stores the images in the components
        themselves. Note that these operations are really heavy.
        """
        self.componentsView.render()

    def draw(self):
        """
        Main function. It is called once per frame by MesaGraphics, in the main thread.
        It refreshes the screen and draws all onto it.
        """
        self.screen.fill((255, 255, 255))
        self.componentsView.draw()  # Draw the components

        # Draw the UI Elements
        for ui in self.ui_elements:
            if ui.visible:
                ui.draw(self.screen)

        if self.ui_focused is not None:
            self.ui_focused.secondary_draw(self.screen)

        # Draw the debug message (if debug is enabled)
        if self.model.debug: self.draw_debug()

        pg.display.flip()  # Refresh the screen with the modifications

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
                self.userParamView.userTweakableModelParams[to_add.name] = to_add
            else:
                self.userParamView.userTweakableEntries[to_add.name] = to_add
        return to_add

    def init_fonts(self):
        """
        Called in the __init__ of View.
        It initializes the pygame.font module, and creates some fonts
        """
        pg.font.init()
        default_path = pg.font.get_default_font()
        self.fonts["basic30"] = pg.font.Font(default_path, 15)
        self.fonts["basic40"] = pg.font.Font(default_path, 20)
        self.fonts["basic30"] = pg.font.Font(default_path, 30)
        self.fonts["basic40"] = pg.font.Font(default_path, 40)

    def quit(self):
        """ End the visualization """
        pg.quit()

    def resize(self, new_size: pg.Vector2):
        ratio = pg.Vector2(new_size.x / self.screen_size.x, new_size.y / self.screen_size.y)
        self.ratio = mul(ratio, self.ratio)
        for ui in self.ui_elements:
            ui.resize(ratio, self.ratio)
        self.userParamView.correct_resizing(ratio)

        self.screen_size = new_size

    def _create_ui(self, name: str, model_params, custom_method_call, play_interval: int, render_interval: int) -> None:
        """
        Instantiate the UI.
        This function creates all the UIElements. This function describe where each element is placed.
        Moreover, the order of creation describe which element is above. The drawer draws them in the order of creation.
        So the last UIElement is the one above the others, and the first one is the one beyond the others.
        """
        self.userParamView.create_ui(model_params, custom_method_call, play_interval, render_interval)
        self._create_up_bar(name)
        self.componentsView.create_ui()

    def _create_up_bar(self, name: str) -> None:
        """ Creates the blue bar on top of the screen, and write the name into it. """
        self.add_UIElement(Rectangle, pg.Vector2(0, 0), pg.Vector2(1280, 37), color=BLUE)
        text = self.add_UIElement(Text, pg.Vector2(0, 0), name, self.fonts["basic30"], color=WHITE)
        text.set_pos(pg.Vector2(40, 20 - text.image.get_height() / 2))  # noqa
        self._create_remove_controls_button()
        self._create_reset_start_step_buttons()

    def _create_remove_controls_button(self) -> None:
        """ Creates the button that toggle or untoggle the control bar. """

        def custom_draw(button, screen):
            bg_color = LIGHT2_BLUE if button.hover else BLUE
            pg.draw.rect(screen, bg_color, pg.Rect(button.pos, button.size), border_radius=10)

            offset = mul(pg.Vector2(5, 5), button.ratio)
            pg.draw.rect(screen, WHITE, pg.Rect(button.pos + offset, button.size - 2 * offset),
                         border_radius=5, width=3)
            pg.draw.line(screen, WHITE, button.pos + offset + pg.Vector2(8, 0),
                         button.pos + offset + pg.Vector2(8, button.size.y - 2 * offset.y - 3), width=3)

        button = self.add_UIElement(Button, pg.Vector2(0, 0), "",
                                    self.fonts["basic30"], name="remove control bar",
                                    custom_draw=custom_draw)
        button.size = mul(pg.Vector2(33, 33), button.ratio)
        button.set_pos(mul(pg.Vector2(2, 2), button.ratio))

    def _create_reset_start_step_buttons(self):
        """ Creates the three buttons in the up bar : RESET, START/STOP and STEP """
        x = 1090
        texts = ("RESET", "START", "STEP")
        names = ("RESET", "START/STOP", "STEP")

        def custom_draw(b, screen):
            b.size = mul(pg.Vector2(60, 31), b.ratio)
            bg_color = LIGHT1_BLUE if b.hover else BLUE
            pg.draw.rect(screen, bg_color, pg.Rect(b.pos, b.size), border_radius=5)
            b.text.pos = b.pos + b.size / 2 - pg.Vector2(*b.text.image.get_size()) / 2
            b.text.draw(screen)

        for i in range(3):
            self.add_UIElement(Button, pg.Vector2(x, 3), texts[i], self.fonts["basic30"], name=names[i],
                               custom_draw=custom_draw, font_color=(255, 255, 255))
            x += 65

    def draw_debug(self):
        """
        This function draws debug information to help programmer, or maybe the user.
        This function is called only if you enter the debug mode by pressing "d".
        """
        texts = []
        for info in self.model.debug_infos:
            texts.append(info + ": " + str(self.model.debug_infos[info]))
        y = 0
        for text in texts:
            image = self.fonts["basic30"].render(text, False, (255, 255, 255), (0, 0, 0, 125))
            self.screen.blit(image, pg.Vector2(0, y))
            y += image.get_height()

    def switch_page(self, new_page: int):
        """
        Switch to another page and update page-selection buttons.

        Resets the page scrolling position.
        """
        self.componentsView.switch_page(new_page)

    def scroll_page(self, amount: int):
        """
        Scroll through the components if there are to many components.
        :param amount: how much the user is scrolling.
        """
        self.componentsView.scroll(amount)


class ComponentsView:
    def __init__(self, view: View, components, renderer=None):
        """
        This class handle the components view. It handles the rendering of components and the pages.
        :param view: The View class, useful because only the View class can create new UI elements.
        :param components: The components sent by the user. They are tuples (component, page), or only the component.
        A component is a function that takes the model, and returns a pygame.Surface/
        :param renderer: The renderer is optional. It is a SpaceRenderer from mesa.visualization.
        """
        self.view = view
        self.max_page_scrolling_y = self.page_scrolling_y = 0
        self.page = 0  # Showed page
        self.min_page = self.max_page = 0  # The minimal page and maximal page existing
        self.min_visible_page = 0  # The minimal switch-page button shown
        self.components = {0: []}
        if components is not None:
            self._store_components(components)
        if renderer is not None:
            self.components[0].insert(0, Component(self.view.model, create_space_component(renderer)))

    def create_ui(self) -> None:
        self.create_switch_page_buttons()

    def draw(self):
        """
        This function draws all the components in the current page.
        """
        y = (40 - self.page_scrolling_y) * self.view.ratio.y
        next_y = y - 55
        default_x = (0, 300)[self.view.userParamView.show_control_bar] * self.view.ratio.x
        x = default_x
        for component in self.components[self.page]:
            image = component.image
            if image is None:
                continue
            size = image.get_size()
            if size[0] + x > 1280 * self.view.ratio.x:
                y = next_y + 10
                next_y = y
                x = default_x
            next_y = max(next_y, y + size[1])
            self.view.screen.blit(image, (x, y))
            x += size[0] + 10
        self.max_page_scrolling_y = max(next_y - 700 * self.view.ratio.y + self.page_scrolling_y * self.view.ratio.y, 0)
        self._page_scroll_clamp()

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
            self.components[page].append(Component(self.view.model, comp))
        self._fill_missing_pages()

    def _fill_missing_pages(self):
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
        for i in range(self.min_page + 1, self.max_page):
            if i not in self.components:
                self.components[i] = []

    def create_switch_page_buttons(self) -> None:
        """
        This function creates the buttons on top of the screen which allow to change the page.
        They are aligned. If there are too many pages, they will be smaller.
        """
        buttons = []

        def custom_page_draw(button, screen):
            if button.locked:
                pg.draw.rect(screen, WHITE, pg.Rect(button.pos, button.size),
                             border_top_left_radius=10, border_top_right_radius=10)
                pg.draw.rect(screen, WHITE, pg.Rect(button.pos + pg.Vector2(-10, button.size.y - 10),
                                                    pg.Vector2(10, 10)))
                pg.draw.rect(screen, WHITE,
                             pg.Rect(button.pos + pg.Vector2(button.size.x, button.size.y - 10), pg.Vector2(10, 10)))
                pg.draw.circle(screen, BLUE, button.pos + pg.Vector2(-10, button.size.y - 10), 10,
                               draw_bottom_right=True)
                pg.draw.circle(screen, BLUE,
                               button.pos + pg.Vector2(button.size.x + 10, button.size.y - 10), 10,
                               draw_bottom_left=True)
            elif button.hover:
                pg.draw.rect(screen, LIGHT2_BLUE,
                             pg.Rect(button.pos + pg.Vector2(5, 5),
                                     button.size - pg.Vector2(10, 12)),
                             border_radius=10)
            button.text.draw(screen)

        if self.max_page + 1 - self.min_page <= 10:
            for i in range(self.min_page, self.max_page + 1):
                buttons.append(
                    self.view.add_UIElement(Button, pg.Vector2(0, 0), f"PAGE {i}", self.view.fonts["basic30"],
                                            custom_draw=custom_page_draw, font_color=WHITE))
            size_x = sum([button.size.x for button in buttons])
            x = (1050 + 300) // 2 - size_x // 2
            for button in buttons:
                button.set_pos(pg.Vector2(x, 0))
                x += button.size.x
                button.size.y = 37

        else:
            if 30 < -self.min_page + self.max_page + 1:
                warnings.warn("There are to many pages, the visualisation could not support it.")
            for i in range(self.min_page, self.max_page + 1):
                buttons.append(self.view.add_UIElement(Button, pg.Vector2(0, 0), f"{i}", self.view.fonts["basic30"],
                                                       custom_draw=custom_page_draw, name=f"PAGE {i}",
                                                       font_color=WHITE))
                x = 310
                button_size_x = (1040 - 310) // len(buttons)
                for button in buttons:
                    button.set_pos(pg.Vector2(x, 0))
                    button.size = pg.Vector2(button_size_x, 37)
                    button.text.pos = button.pos + button.size // 2 - pg.Vector2(button.text.image.get_size()) // 2
                    x += button_size_x

        self.switch_page(self.page)

    def switch_page(self, new_page):
        """ Change the current page """
        self.view.buttons[f"PAGE {self.page}"].unlock()
        self.view.buttons[f"PAGE {self.page}"].modify_text(f"PAGE {self.page}", color=(255, 255, 255))
        self.view.buttons[f"PAGE {self.page}"].size.y = 37 * self.view.buttons[f"PAGE {self.page}"].ratio.y
        self.page = new_page
        self.view.buttons[f"PAGE {self.page}"].lock()
        self.view.buttons[f"PAGE {self.page}"].modify_text(f"PAGE {self.page}", color=(0, 0, 0))
        self.view.buttons[f"PAGE {self.page}"].size.y = 37 * self.view.buttons[f"PAGE {self.page}"].ratio.y
        # Changer le texte change aussi la taille du bouton, on doit la remodifier manuellement

        self.page_scrolling_y = 0

    def _page_scroll_clamp(self):
        if self.page_scrolling_y <= 0:
            self.page_scrolling_y = 0
        elif self.page_scrolling_y >= self.max_page_scrolling_y / self.view.ratio.y:
            self.page_scrolling_y = self.max_page_scrolling_y / self.view.ratio.y

    def render(self):
        """
        Renders all the component images according to the model state. It stores the images in the components
        themselves. Note that these operations are really heavy.
        """
        for component in self.components[self.page]:
            component.render()

    def scroll(self, amount: int):
        self.page_scrolling_y += amount * self.view.SCROLL_SENSIBILITY
        self._page_scroll_clamp()


class UserParamView:
    def __init__(self, view):
        self.view = view
        self.max_param_scrolling_y = self.param_scrolling_y = 0
        self.scrollable_elements = []  # There are all the elements that you can move scrolling through the parameter window
        self.hideable_elements = []  # List of the UI elements that should be hided when you untoggle the control bar.
        self.userTweakableModelParams = {}  # Provide fast and easy access to user's Model parameters
        self.userTweakableEntries = {}
        self.show_control_bar = True

    def create_ui(self, model_params, custom_method_call, play_interval: int, render_interval: int) -> None:
        """
        This function creates the grey column in the left part of the screen, and fills it with the user parameters.
        It creates also the 3 buttons RESET, START/STOP, and STEP
        """
        rect = self.view.add_UIElement(Rectangle, pg.Vector2(0, 37), pg.Vector2(300, 703), color=LIGHT_GRAY)
        self.hideable_elements.append(rect)
        width = 5
        shadow = self.view.add_UIElement(Shadow, pg.Vector2(300 - width, 37), pg.Vector2(300 - width, 740),
                                         pg.Vector2(1, 0),
                                         width)
        self.hideable_elements.append(shadow)
        self._create_flow_control_entries(play_interval, render_interval)
        y = 260
        if model_params is not None:
            y = self._create_model_params_entries(model_params) + 50
        if custom_method_call is not None:
            self._create_custom_method_call_entries(custom_method_call, y)

    def toggle_untoggle_control_bar(self):
        self.show_control_bar = not self.show_control_bar
        for elt in self.hideable_elements:
            elt.visible = self.show_control_bar

    def correct_resizing(self, ratio):
        for elt in self.scrollable_elements:
            p = elt.pos + pg.Vector2(0, self.param_scrolling_y * ratio.y)
            elt.set_pos(p)

        self.param_scrolling_y = 0

    def scroll_params(self, amount: int):
        """
        Scroll through the parameters if there are to many parameters.
        :param amount: how much the user is scrolling.
        """
        prev_param_scrolling_y = self.param_scrolling_y
        self.param_scrolling_y += amount * self.view.SCROLL_SENSIBILITY
        self._param_scroll_clamp()
        amount = self.param_scrolling_y - prev_param_scrolling_y
        for element in self.scrollable_elements:
            element.set_pos(element.pos - pg.Vector2(0, amount))

    def _param_scroll_clamp(self):
        if self.param_scrolling_y <= 0:
            self.param_scrolling_y = 0
        elif self.param_scrolling_y >= self.max_param_scrolling_y * self.view.ratio.y:
            self.param_scrolling_y = self.max_param_scrolling_y * self.view.ratio.y

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
            text = self.view.add_UIElement(Text, pg.Vector2(10, y), label, self.view.fonts["basic40"], color=BLACK)
            self.hideable_elements.append(text)
            self.scrollable_elements.append(text)
        return text.image.get_width() + 20, y + text.image.get_height() / 2, text  # noqa

    def _split_label(self, label: str):
        """ Split the labels so that only max_number_chars characters are in any line. """
        max_number_chars = 26
        res = []
        words = label.split(" ")
        i = -1
        last_chosen_i = 0
        current_size = 0
        while i + 1 < len(words):
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
        for j in range(last_chosen_i, i + 1):
            r += words[j] + " "
        res.append(r[:-1])
        return res

    def _create_model_params_entries(self, model_params) -> int:
        """
        Create the tweakable user parameters in the left column, which describe how to re-instantiate the model using
        the RESET button.
        Returns the y position of the bottom of the model param entries.
        """
        starting_y = y = 260
        card = self.view.add_UIElement(ShadowedCard, pg.Vector2(5, y - 10), pg.Vector2(285, 10), WHITE, 3, border_radius=10)
        for param_name in model_params:
            y = self._create_user_param(param_name, model_params[param_name], y)
        y += 15

        self.scrollable_elements.append(card)
        self.hideable_elements.append(card)
        card.set_size(pg.Vector2(285, y - starting_y))

        self.max_param_scrolling_y = max(y - 700, 0)
        return y

    def _create_custom_method_call_entries(self, custom_method_call, starting_y) -> None:
        y = starting_y
        for method_name in custom_method_call:
            starting_y = y
            card = self.view.add_UIElement(ShadowedCard, pg.Vector2(5, y - 10), pg.Vector2(285, 10), WHITE, 3, border_radius=10)
            button = self.view.add_UIElement(Button, pg.Vector2(15, y), method_name, self.view.fonts["basic30"],
                                             name=f"method_call-{method_name}")
            self.hideable_elements.append(button)
            self.scrollable_elements.append(button)
            y += button.size.y + 5
            params = custom_method_call[method_name]
            for param_name in params:
                params[param_name]["model_param"] = False
                params[param_name]["associated_method"] = method_name
                y = self._create_user_param(param_name, params[param_name], y)
            y += 15

            card.set_size(pg.Vector2(285, y - starting_y))
            self.hideable_elements.append(card)
            self.scrollable_elements.append(card)
            y += 50
        y -= 50
        self.max_param_scrolling_y = max(y - 700, 0)

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
            x = 15
            y += lastUiElement.image.get_height()
            args = self._compute_args_for_user_params_creation(type, x, y)
            elem = self.view.add_UIElement(type, *args, **param)
            self.hideable_elements.append(elem)
            self.scrollable_elements.append(elem)

            y += 30

        return y

    def _create_flow_control_entries(self, play_interval: int, render_interval: int) -> None:
        """
        Create the flow control user parameters. Thus are the two sliders "play interval" and "render interval".
        :param play_interval: The starting value of the play_interval's slider
        :param render_interval: The starting value of the render_interval's slider
        """
        starting_y = y = 90
        card = self.view.add_UIElement(ShadowedCard, pg.Vector2(5, y - 10), pg.Vector2(285, 10), WHITE, 3, border_radius=10)
        self.scrollable_elements.append(card)
        self.hideable_elements.append(card)
        play_interval_params = {
            "type": "SliderInt",
            "min": 0,
            "max": 2000,
            "step": 10,
            "value": play_interval,
            "param_name": "play_interval",
            "label": "Play interval (ms):",
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
            "label": "Render interval (steps): ",
            "model_param": False
        }
        y = self._create_user_param("render_interval", render_interval_params, y)
        card.set_size(pg.Vector2(285, y - starting_y))

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
            elif t == "Select":
                return Select, param
            elif t == "InputText":
                return InputText, param
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
            return pg.Vector2(x, y), 280 - x
        elif t == Checkbox:
            return (pg.Vector2(x, y - Checkbox.SIZE.y / 2 * self.view.ratio.y),)
        elif t == Select:
            return (pg.Vector2(x, y),)
        elif t == InputText:
            return (pg.Vector2(x, y),)
