from mesa_graphics.UIText import Text
from mesa_graphics.BoundingElement import *


class Card(BoundingElement):
    """
    Inspired by the Solara's Card, this class is like a container of graphical components.
    It decides directly where to place them
    """
    BORDER_SIZE = 0.01
    BORDER_RADIUS_RATIO = 0.005

    def __init__(self, boundaries, pos: pg.Vector2, size: pg.Vector2):
        """ The positions are between 0 and 1: (0,0) is the top left corner, and (1, 1) is the bottom right corner"""
        self.pos = pos
        self.size = size
        self.boundaries = boundaries
        assert self.pos.x >= 0 and self.pos.x + self.size.x <= 1 and self.pos.y >= 0 and self.pos.y + self.size.y <= 1, \
            "The Card shall be onto the screen"
        self.components = []
        self.ui_elements = []
        self.real_size = self.size
        self.scroll_level = 0

    def add_text(self, pos, size, text, textcolor=(0, 0, 0), bg_color=None):
        self.ui_elements.append(Text(self, pos, size, text, textcolor, bg_color))

    def get_size(self):
        return mul(sub(self.size, self.BORDER_SIZE), self.boundaries.get_size())

    def get_pos(self):
        return self.boundaries.get_relative(self.pos)

    def draw(self, screen):
        self.draw_background(screen)
        for ui_element in self.ui_elements:
            ui_element.draw(screen)
        for component in self.components:
            component.draw(screen)

    def draw_background(self, screen):
        rad = int(self.BORDER_RADIUS_RATIO * (self.boundaries.get_width() + self.boundaries.get_height()) / 2)
        pos1 = mul(self.pos, self.boundaries.get_size())
        size1 = mul(self.size, self.boundaries.get_size())
        pos2 = mul(self.pos, self.boundaries.get_size()) + pg.Vector2(1, 1)
        size2 = (mul(self.size + pg.Vector2(-self.BORDER_SIZE, -self.BORDER_SIZE), self.boundaries.get_size()) -
                 pg.Vector2(1, 1))

        pg.draw.rect(screen, (180, 180, 180), pg.Rect(pos1, size1), 0, rad, rad, rad, rad)
        pg.draw.rect(screen, (255, 255, 255), pg.Rect(pos2, size2), 0, rad, rad, rad, rad)

