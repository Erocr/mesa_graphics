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
        self.ui_elements = []
        self.create_ui()

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
        self.ui_elements += self._create_up_bar() + self._create_controls() + self._create_switch_page_buttons()

    def _create_up_bar(self):
        return [
            Rectangle(pg.Vector2(0, 0), pg.Vector2(1280, 80), (0, 80, 255)),
            Text(pg.Vector2(80, 0), self.name)
        ]

    def _create_controls(self):
        res = [
            Rectangle(pg.Vector2(0, 80), pg.Vector2(300, 660), (220, 220, 220)),
            Text(pg.Vector2(20, 80), "Controls")
        ]
        x = 20
        texts = ("RESET", "START", "STEP")

        def reset_action():
            print("reset")

        def step_action():
            self.model.mesa_model.step()

        actions = (reset_action, None, step_action)
        for i in range(3):
            res.append(UIButton(pg.Vector2(x, 120), texts[i], actions[i], font_size=15))
            x += res[-1].text.image.get_width() + 30

        start_stop_button = res[-2]

        def start_or_stop_action():
            self.model.is_playing = not self.model.is_playing
            start_stop_button.modify_text(("START", "STOP")[self.model.is_playing])

        start_stop_button.set_action(start_or_stop_action)
        return res

    def _create_switch_page_buttons(self):
        buttons = []
        for i in range(self.min_page, self.max_page+1):
            def switch_page(i):
                def res():
                    self.page = i
                return res
            buttons.append(UIButton(pg.Vector2(0, 0), f"PAGE {i}", switch_page(i), font_size=15))
        size_x = sum([button.size.x for button in buttons]) + 10 * (len(buttons) - 1)
        x = (1280 + 300) // 2 - size_x // 2
        for button in buttons:
            button.set_pos(pg.Vector2(x, 90))
            x += button.size.x + 10
        return buttons

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

