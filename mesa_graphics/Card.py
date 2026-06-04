import pygame as pg
from mesa_graphics.math import *
from mesa_graphics.UIText import Text


class Card:
    """
    Inspired by the Solara's Card, this class is like a container of graphical components.
    It decides directly where to place them
    """
    BORDER_SIZE = 0.01
    BORDER_RADIUS_RATIO = 0.005

    def __init__(self, pos: pg.Vector2, size: pg.Vector2, screen):
        """ The positions are between 0 and 1: (0,0) is the top left corner, and (1, 1) is the bottom right corner"""
        self.pos = pos
        self.size = size
        self.screen = screen
        assert self.pos.x >= 0 and self.pos.x + self.size.x <= 1 and self.pos.y >= 0 and self.pos.y + self.size.y <= 1, \
            "The Card shall be onto the screen"
        self.components = []
        self.ui_elements = []
        self.real_size = self.size
        self.scroll_level = 0

    def add_text(self, pos, size, text, textcolor=(0, 0, 0), bg_color=None):
        self.ui_elements.append(Text(self.screen, pos, size, text, textcolor, bg_color))

    def get_size(self):
        return ((self.size.x - self.BORDER_SIZE) * self.screen.get_width(),
                (self.size.y - self.BORDER_SIZE) * self.screen.get_height())

    def get_pos(self):
        return self.pos.x * self.screen.get_width(), self.pos.y * self.screen.get_width()

    def draw(self):
        self.draw_background()
        for ui_element in self.ui_elements:
            ui_element.draw(self)
        for component in self.components:
            component.draw(self)

    def draw_background(self):
        rad = int(self.BORDER_RADIUS_RATIO * (self.screen.get_width() + self.screen.get_height()) / 2)
        pos1 = ratio_to_px(self.pos, self.screen)
        size1 = ratio_to_px(self.size, self.screen)
        pos2 = ratio_to_px(self.pos, self.screen) + pg.Vector2(1, 1)
        size2 = ratio_to_px(self.size + pg.Vector2(-self.BORDER_SIZE, -self.BORDER_SIZE), self.screen) - pg.Vector2(1, 1)

        pg.draw.rect(self.screen, (180, 180, 180), pg.Rect(pos1, size1), 0, rad, rad, rad, rad)
        pg.draw.rect(self.screen, (255, 255, 255), pg.Rect(pos2, size2), 0, rad, rad, rad, rad)

