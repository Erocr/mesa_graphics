from pygame import Vector2


class UIElement:
    def __init__(self, screen, pos: Vector2, size: Vector2):
        self.pos = pos
        self.size = size
        self.screen = screen

    def draw(self, card):
        assert False, "This is an abstract class"

