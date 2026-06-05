import pygame as pg
from mesa_graphics.UIElement import UIElement


class Text(UIElement):
    FONT = None

    def __init__(self, boundaries, pos, size, text, color=(0, 0, 0), bg_color=None):
        if Text.FONT is None:
            Text.FONT = pg.font.Font('freesansbold.ttf', 64)
        super().__init__(boundaries, pos, size)
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.text_image = None
        self.draw_pos = None

    def draw(self, screen):
        if self.text_image is None or self.need_update(pg.Vector2(self.text_image.get_size())):
            self.render_text()
        self.draw_image(screen, self.text_image)

    def render_text(self):
        image = self.FONT.render(self.text, False, self.color, self.bg_color)
        self.text_image = self.scale(image)
