from mesa_graphics.math import * 


class BoundingElement:
    def get_pos(self) -> pg.Vector2:
        assert False, "It is an abstract method"

    def get_size(self) -> pg.Vector2:
        assert False, "It is an abstract method"

    def get_width(self):
        return self.get_size().x

    def get_height(self):
        return self.get_size().y

    def get_relative(self, relative_pos):
        return self.get_pos() + mul(relative_pos, self.get_size())


class ScreenBounds(BoundingElement):
    def __init__(self, screen):
        self.screen = screen

    def get_pos(self) -> pg.Vector2:
        return pg.Vector2(0, 0)

    def get_size(self) -> pg.Vector2:
        return pg.Vector2(self.screen.get_size())
