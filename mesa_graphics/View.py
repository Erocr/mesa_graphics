from mesa_graphics.UIElement import *


class View:
    def __init__(self, model, components=None, name=None):
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
            self.components = {}
            self.store_components(components)
        self.buttons = {}  # Provide fast and easy access to buttons
        self.ui_elements = []
        self.create_ui()

    def add_UIElement(self, type, *args, **kwargs):
        to_add = type(*args, **kwargs)
        self.ui_elements.append(to_add)
        if isinstance(to_add, UIButton):
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

    def create_ui(self):
        self._create_up_bar()
        self._create_controls()
        self._create_switch_page_buttons()

    def _create_up_bar(self):
        self.add_UIElement(Rectangle, pg.Vector2(0, 0), pg.Vector2(1280, 80), (0, 80, 255))
        self.add_UIElement(Text, pg.Vector2(80, 0), self.name)

    def _create_controls(self):
        self.add_UIElement(Rectangle, pg.Vector2(0, 80), pg.Vector2(300, 660), (220, 220, 220))
        self.add_UIElement(Text, pg.Vector2(20, 80), "Controls")
        x = 20
        texts = ("RESET", "START", "STEP")
        names = ("RESET", "START/STOP", "STEP")

        for i in range(3):
            button = self.add_UIElement(UIButton, pg.Vector2(x, 120), texts[i], font_size=15, name=names[i])
            x += button.text.image.get_width() + 30

    def _create_switch_page_buttons(self):
        buttons = []
        for i in range(self.min_page, self.max_page+1):
            buttons.append(self.add_UIElement(UIButton, pg.Vector2(0, 0), f"PAGE {i}", font_size=15))
        size_x = sum([button.size.x for button in buttons]) + 10 * (len(buttons) - 1)
        x = (1280 + 300) // 2 - size_x // 2
        for button in buttons:
            button.set_pos(pg.Vector2(x, 90))
            x += button.size.x + 10

    def draw(self):
        self.screen.fill((255, 255, 255))
        for ui in self.ui_elements:
            ui.draw(self.screen)
        self.draw_components()
        pg.display.flip()

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

