import pygame as pg
from mesa_graphics.UIElement import UIElement
from mesa_graphics.math import ratio_to_px, px_to_ratio


class Text(UIElement):
    FONT = None

    def __init__(self, screen, pos, size, text, color=(0, 0, 0), bg_color=None):
        if Text.FONT is None:
            Text.FONT = pg.font.Font('freesansbold.ttf', 64)
        super().__init__(screen, pos, size)
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.text_image = None
        self.draw_pos = None

    def draw(self, card):
        size = ratio_to_px(self.size, card)
        if self.text_image is None or size.distance_squared_to(self.text_image.get_size()) > 4:
            self.render_text(card)
        self.screen.blit(self.text_image, ratio_to_px(self.draw_pos + pg.Vector2(card.get_pos()), card))

    def render_text(self, card):
        image = self.FONT.render(self.text, False, self.color, self.bg_color)
        im_size = pg.Vector2(image.get_size())
        size = ratio_to_px(self.size, card)
        scale_factor = min(size.x / im_size.x, size.y / im_size.y)
        self.text_image = pg.transform.scale_by(image, scale_factor)
        im_size = im_size * scale_factor
        self.draw_pos = self.pos + px_to_ratio((size - im_size) * 0.5, card)
