from mesa_graphics.math import *
from mesa_graphics.BoundingElement import BoundingElement


class UIElement(BoundingElement):
    def __init__(self, boundaries, pos: pg.Vector2, size: pg.Vector2):
        self.pos = pos
        self.size = size
        self.boundaries = boundaries

    def get_pos(self) -> pg.Vector2:
        return self.boundaries.get_relative(self.pos)

    def get_size(self) -> pg.Vector2:
        return mul(self.boundaries.get_size(), self.size)

    def draw(self, card):
        assert False, "This is an abstract class"

    def need_update(self, current_px_size):
        b_size = self.get_size()
        return not (current_px_size.x <= b_size.x and current_px_size.y <= b_size.y and
                    (current_px_size.x == b_size.x or current_px_size.y == b_size.y))

    def scale_factor(self, current_px_size):
        b_size = self.get_size()
        return min(b_size.x / current_px_size.x, b_size.y / current_px_size.y)

    def scale(self, image):
        im_size = pg.Vector2(image.get_size())
        scale_factor = self.scale_factor(im_size)
        image_res = pg.transform.scale_by(image, scale_factor)
        return image_res

    def draw_image(self, screen, image):
        draw_pos = self.boundaries.get_relative(self.pos) + (self.get_size() - pg.Vector2(image.get_size())) * 0.5
        screen.blit(image, draw_pos)

