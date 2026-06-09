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


class Button(UIElement):
    alreadyUsed = set()

    def __init__(self, pos, text: str, font_size=32, name=None):
        """
        :param pos:
        :param text:
        :param font_size:
        :param name: Un identifiant pour le reconnaître
        """
        super().__init__(pos)
        self.font_size = font_size
        self.text = Text(pos+pg.Vector2(10, 10), text, font_size)
        self.size = pg.Vector2(self.text.image.get_size()) + pg.Vector2(20, 20)
        self.hover = False
        if name is None:
            name = text
        if name in self.alreadyUsed:
            i = 0
            new_name = f"{name}{i}"
            while new_name is self.alreadyUsed:
                i += 1
                new_name = f"{name}{i}"
            name = new_name
        self.name = name

    def draw(self, screen):
        bg_color = (200, 200, 200) if self.hover else (180, 180, 180)
        pg.draw.rect(screen, bg_color, pg.Rect(self.pos, self.size))
        self.text.draw(screen)

    def modify_text(self, new_text, font_size=None):
        if font_size is None:
            font_size = self.font_size
        self.text = Text(self.pos + pg.Vector2(10, 10), new_text, font_size)
        self.size = pg.Vector2(self.text.image.get_size()) + pg.Vector2(20, 20)

    def set_pos(self, pos):
        self.pos = pos
        self.text.set_pos(pos+pg.Vector2(10, 10))


class Slider(UIElement):
    CIRCLE_RADIUS = 5
    BAR_HEIGHT = 2

    def __init__(self, t, pos, length, value=None, min=0, max=10, step=1):
        assert min <= max, "min shall be less than max"
        assert t in ("SliderInt", "SliderFloat"), f"type {t} is unknown"
        super().__init__(pos)
        self.length = length
        self.selectedPosX = 0
        self.min = min
        self.max = max
        self.value = None
        if value is None: value = (min + max) / 2
        self.set_value(value)
        self.step = step
        self.hover = False
        self.type = t

    def draw(self, screen):
        pg.draw.rect(screen, (0, 50, 255), pg.Rect(self.pos - pg.Vector2(0, self.BAR_HEIGHT//2),
                                                   pg.Vector2(self.length, self.BAR_HEIGHT)))
        circle_color = (0, 150, 255) if self.hover else (0, 50, 255)
        pg.draw.circle(screen, circle_color, pg.Vector2(self.selectedPosX, self.pos.y), self.CIRCLE_RADIUS)
        if self.hover:
            font = pg.font.Font('freesansbold.ttf', 15)
            if self.type == "SliderInt":
                text = str(self.value)
            else:
                text = f"{self.value:.2f}"
            image = font.render(text, False, (255, 255, 255), (0, 0, 0, 125))
            screen.blit(image, pg.Vector2(self.selectedPosX-image.get_width()/2, self.pos.y+self.CIRCLE_RADIUS))

    def set_value(self, value):
        value = min(max(value, self.min), self.max)
        self.selectedPosX = (value - self.min) / (self.max - self.min) * self.length + self.pos.x
        self.value = value

