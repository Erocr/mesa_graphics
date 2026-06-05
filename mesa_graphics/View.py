from mesa_graphics.UIElement import *


class View:
    def __init__(self, model, name=None):
        pg.font.init()
        self.screen = pg.display.set_mode((1280, 740), pg.RESIZABLE)
        self.model = model
        self.name = name
        if name is None:
            self.name = type(self.model).__name__
        self.ui_elements = []
        self.create_ui()

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
        for text in ("RESET", "▶", "STEP"):
            res.append(UIButton(pg.Vector2(x, 120), text, font_size=15))
            x += res[-1].text.image.get_width() + 30
        return res

    def draw(self):
        self.screen.fill((255, 255, 255))
        for ui in self.ui_elements:
            ui.draw(self.screen)
        pg.display.flip()
