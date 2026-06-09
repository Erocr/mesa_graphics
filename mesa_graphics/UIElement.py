import pygame as pg


class UIElement:
    def __init__(self, pos):
        """ It is an abstract class describing an element of UI. """
        self.pos = pos

    def draw(self, screen):
        """ This function draws the UIElement onto the screen. """
        assert False, "this is an abstract method"


class Rectangle(UIElement):
    def __init__(self, pos, size, color=(255, 255, 255)):
        """
        :param pos: The top-left corner position. It must be a pg.Vector2.
        :param size: The size of the rectangle. It must be a pg.Vector2.
        :param color: The filling color. It is a tuple (r, g, b).
        """
        super().__init__(pos)
        self.size = size
        self.color = color

    def draw(self, screen):
        pg.draw.rect(screen, self.color, pg.Rect(self.pos, self.size))


class Text(UIElement):
    def __init__(self, pos, text, font_size=32):
        """
        :param pos: The top-left corner position. It must be a pg.Vector2
        :param text: The string shown
        :param font_size: The font size
        """
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
        The logic for drawing a clickable button.

        :param pos: The top-left corner position. It must be a pg.Vector2.
        :param text: The string shown in the button.
        :param font_size: The font size of the text in the button.
        :param name: An identification. It is used to associate actions in the Controller.
        If no name is given, the name is the text. If the text is already used, it will put a number
        right after the text.
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
        """
        Modifies the text written in the button.
        :param new_text: the new string to show.
        :param font_size: The new font_size. If you don't put the font size, it will put the font_size
        given at the creation of the instance.
        """
        if font_size is None:
            font_size = self.font_size
        self.text = Text(self.pos + pg.Vector2(10, 10), new_text, font_size)
        self.size = pg.Vector2(self.text.image.get_size()) + pg.Vector2(20, 20)

    def set_pos(self, pos):
        """ Change the position of the button. """
        self.pos = pos
        self.text.set_pos(pos+pg.Vector2(10, 10))


class Slider(UIElement):
    CIRCLE_RADIUS = 5
    BAR_HEIGHT = 2

    def __init__(self, t, pos, length, value=None, min=0, max=10, step=0.01):
        """
        This class handle the logic for drawing a slider.

        :param t: The type of the slider, it can be "SliderInt" or "SliderFloat"
        :param pos: A pg.Vector2 describing the left position of the slider.
        :param length: The length of the bar of the slider.
        :param value: The initial value. If None, value is initialized with the middle value.
        :param min: The minimum value it can take.
        :param max: The maximum value it can take.
        :param step: The step between two possible values.
        """
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

