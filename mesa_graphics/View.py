from mesa_graphics.UIElement import *
from mesa_graphics.matplotlib_components import create_space_component
from time import time


class View:
    def __init__(self, model, renderer=None, components=None, model_params=None, name=None):
        pg.font.init()
        self.screen = pg.display.set_mode((1280, 740), pg.RESIZABLE)
        self.model = model
        self.name = name
        if name is None:
            self.name = type(self.model).__name__
        self.page = 0
        self.min_page = self.max_page = 0
        if components is None:
            self.components = {0: []}
        else:
            self.components = {0: []}
            self.store_components(components)
        if renderer is not None:
            self.components[0].insert(0, create_space_component(renderer))
        self.buttons = {}  # Provide fast and easy access to buttons
        self.sliders = {}  # Provide fast and easy access to sliders
        self.ui_elements = []
        self.create_ui(model_params)

    def add_UIElement(self, type, *args, **kwargs):
        to_add = type(*args, **kwargs)
        self.ui_elements.append(to_add)
        if isinstance(to_add, Button):
            self.buttons[to_add.name] = to_add
        return to_add

    def store_components(self, components):
        for comp_page in components:
            comp, page = comp_page
            if page not in self.components:
                self.components[page] = []
            self.components[page].append(comp)
        self.add_unuseful_pages()

    def add_unuseful_pages(self):
        self.min_page = 0
        self.max_page = 0
        for page in self.components:
            if page < self.min_page: self.min_page = page
            if page > self.max_page: self.max_page = page
        for i in range(self.min_page+1, self.max_page):
            if i not in self.components:
                self.components[i] = []

    def create_ui(self, model_params):
        self._create_up_bar()
        self._create_switch_page_buttons()
        self._create_controls()
        if model_params is not None:
            self._create_model_params_entries(model_params)

    def _create_up_bar(self):
        self.add_UIElement(Rectangle, pg.Vector2(0, 0), pg.Vector2(1280, 80), (0, 80, 255))
        self.add_UIElement(Text, pg.Vector2(80, 0), self.name)

    def _create_controls(self):
        self.add_UIElement(Rectangle, pg.Vector2(0, 80), pg.Vector2(300, 660), (220, 220, 220))
        x = 1050
        texts = ("RESET", "START", "STEP")
        names = ("RESET", "START/STOP", "STEP")

        for i in range(3):
            button = self.add_UIElement(Button, pg.Vector2(x, 22), texts[i], font_size=15, name=names[i])
            x += button.text.image.get_width() + 30

    def _create_switch_page_buttons(self):
        buttons = []
        for i in range(self.min_page, self.max_page+1):
            buttons.append(self.add_UIElement(Button, pg.Vector2(0, 0), f"PAGE {i}", font_size=15))
        size_x = sum([button.size.x for button in buttons]) + 10 * (len(buttons) - 1)
        x = (1280 + 300) // 2 - size_x // 2
        for button in buttons:
            button.set_pos(pg.Vector2(x, 90))
            x += button.size.x + 10

    def _create_model_params_entries(self, model_params):
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
        text = self.add_UIElement(Text, pg.Vector2(10, y), label, font_size=20)
        return text.image.get_width() + 20, y+text.image.get_height()/2, text

    def draw(self):
        start = time()
        self.screen.fill((255, 255, 255))
        for ui in self.ui_elements:
            ui.draw(self.screen)
        self.draw_components()
        if self.model.debug: self.draw_debug()
        pg.display.flip()
        self.model.debug_infos["viewer_time"] = time() - start

    def draw_components(self):
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
        texts = []
        for info in self.model.debug_infos:
            texts.append(info + ": " + str(self.model.debug_infos[info]))
        font = pg.font.Font('freesansbold.ttf', 15)
        y = 0
        for text in texts:
            image = font.render(text, False, (255, 255, 255), (0, 0, 0, 125))
            self.screen.blit(image, pg.Vector2(0, y))
            y += image.get_height()

