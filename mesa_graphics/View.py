from mesa_graphics.UIElement import *


class View:
    def __init__(self, model, components=None, name=None):
        pg.font.init()
        self.screen = pg.display.set_mode((1280, 740), pg.RESIZABLE)
        self.model = model
        self.name = name
        if name is None:
            self.name = type(self.model).__name__
        self.ui_elements = []
        self.create_ui()
        self.page = 0
        if components is None:
            self.components = {0: []}
        else:
            self.components = {}
            self.store_components(components)

    def store_components(self, components):
        for comp_page in components:
            comp, page = comp_page
            if page not in self.components:
                self.components[page] = []
            self.components[page].append(comp)

    def create_ui(self):
        self.ui_elements += self._up_bar() + self._controls()

    def _up_bar(self):
        return [
            Rectangle(pg.Vector2(0, 0), pg.Vector2(1280, 80), (0, 80, 255)),
            Text(pg.Vector2(80, 0), self.name)
        ]

    def _controls(self):
        res = [
            Rectangle(pg.Vector2(0, 80), pg.Vector2(300, 660), (220, 220, 220)),
            Text(pg.Vector2(20, 80), "Controls")
        ]
        x = 20
        texts = ("RESET", "start", "STEP")

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
            start_stop_button.modify_text(("start", "stop")[self.model.is_playing])

        start_stop_button.set_action(start_or_stop_action)
        return res

    def draw(self):
        self.screen.fill((255, 255, 255))
        for ui in self.ui_elements:
            ui.draw(self.screen)
        self.draw_components()
        pg.display.flip()

    def draw_components(self):
        y = 80
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

