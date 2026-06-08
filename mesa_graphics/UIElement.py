import pygame as pg


class UIElement:
    def __init__(self, pos):
        self.pos = pos

    def draw(self, screen):
        assert False, "this is an abstract method"


class Rectangle(UIElement):
    def __init__(self, pos, size, color):
        super().__init__(pos)
        self.size = size
        self.color = color

    def draw(self, screen):
        pg.draw.rect(screen, self.color, pg.Rect(self.pos, self.size))


class Text(UIElement):
    def __init__(self, pos, text, font_size=32):
        super().__init__(pos)
        font = pg.font.Font('freesansbold.ttf', font_size)
        self.image = font.render(text, False, (0, 0, 0))

    def draw(self, screen):
        screen.blit(self.image, self.pos)

    def set_pos(self, pos):
        self.pos = pos


class UIButton(UIElement):
    def __init__(self, pos, text: str, action, font_size=32):
        super().__init__(pos)
        self.font_size = font_size
        self.text = Text(pos+pg.Vector2(10, 10), text, font_size)
        self.size = pg.Vector2(self.text.image.get_size()) + pg.Vector2(20, 20)
        self.hover = False
        self.action = action

    def draw(self, screen):
        bg_color = (200, 200, 200) if self.hover else (180, 180, 180)
        pg.draw.rect(screen, bg_color, pg.Rect(self.pos, self.size))
        self.text.draw(screen)

    def modify_text(self, new_text, font_size=None):
        if font_size is None:
            font_size = self.font_size
        self.text = Text(self.pos + pg.Vector2(10, 10), new_text, font_size)
        self.size = pg.Vector2(self.text.image.get_size()) + pg.Vector2(20, 20)

    def set_action(self, action):
        self.action = action

    def set_pos(self, pos):
        self.pos = pos
        self.text.set_pos(pos+pg.Vector2(10, 10))

