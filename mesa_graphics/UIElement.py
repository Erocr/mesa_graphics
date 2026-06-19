from typing import Callable
from math import log10

import pygame as pg


class UIElement:
    def __init__(self, pos: pg.Vector2, visible=True):
        """ It is an abstract class describing an element of UI. """
        self.pos = pos
        self._visible = True

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, vis):
        self._visible = vis

    def draw(self, screen: pg.Surface):
        """ This function draws the UIElement onto the screen. """
        assert False, "this is an abstract method"


class Rectangle(UIElement):
    def __init__(self, pos: pg.Vector2, size: pg.Vector2, color=(255, 255, 255)):
        """
        :param pos: The top-left corner position. It must be a pg.Vector2.
        :param size: The size of the rectangle. It must be a pg.Vector2.
        :param color: The filling color. It is a tuple (r, g, b).
        """
        super().__init__(pos)
        self.size = size
        self.color = color

    def draw(self, screen: pg.Surface):
        if self.visible:
            pg.draw.rect(screen, self.color, pg.Rect(self.pos, self.size))


class Shadow(UIElement):
    def __init__(self, p1, p2, direction, length, initial_color=(0, 0, 0), final_color=(255, 255, 255),
                 curved_border_1=False, curved_border_2=False):
        super().__init__(p1)
        self.p1 = p1
        self.p2 = p2
        self.dir = direction.normalize()
        self.length = length
        self.initial_color = pg.Vector3(initial_color)
        self.final_color = pg.Vector3(final_color)
        self.curved_border_1 = curved_border_1
        self.curved_border_2 = curved_border_2

    def draw(self, screen):
        for i in range(self.length):
            color = self.initial_color + (self.final_color - self.initial_color) * i / self.length
            dir_v = (self.p2 - self.p1).normalize()
            cb1 = dir_v * self.curved_border_1 * i
            cb2 = -dir_v * self.curved_border_2 * i
            pg.draw.line(screen, color, self.p1 + i * self.dir + cb1, self.p2 + i * self.dir + cb2)


class Text(UIElement):
    def __init__(self, pos: pg.Vector2, text: str, font_size=32):
        """
        :param pos: The top-left corner position. It must be a pg.Vector2
        :param text: The string shown
        :param font_size: The font size
        """
        super().__init__(pos)
        font = pg.font.Font(pg.font.match_font("liberationmono"), font_size)
        self.image = font.render(text, False, (0, 0, 0))

    def draw(self, screen: pg.Surface):
        if self.visible:
            screen.blit(self.image, self.pos)

    def set_pos(self, pos: pg.Vector2):
        self.pos = pos


class Button(UIElement):
    alreadyUsed = set()

    def __init__(self, pos, text: str, font_size=32, name=None, custom_draw: Callable = None):
        """
        The logic for drawing a clickable button.

        :param pos: The top-left corner position. It must be a pg.Vector2.
        :param text: The string shown in the button.
        :param font_size: The font size of the text in the button.
        :param name: An identification. It is used to associate actions in the Controller.
        :param custom_draw: A function that take the button and the screen, and draw the button on the screen.
        If no name is given, the name is the text. If the name is already used, it will put a number
        right after it.
        """
        super().__init__(pos)
        self.font_size = font_size
        self.text = Text(pos+pg.Vector2(10, 10), text, font_size)
        self.size = pg.Vector2(self.text.image.get_size()) + pg.Vector2(20, 20)
        self.custom_draw = custom_draw
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
        self.locked = False

    def draw(self, screen: pg.Surface):
        if self.visible:
            if self.custom_draw:
                self.custom_draw(self, screen)
            else:
                bg_color = (200, 200, 200) if self.hover else (180, 180, 180)
                if self.locked:
                    bg_color = (0, 80, 255)
                pg.draw.rect(screen, bg_color, pg.Rect(self.pos, self.size))
                self.text.draw(screen)

    def modify_text(self, new_text: str, font_size=None):
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

    def set_pos(self, pos: pg.Vector2):
        """ Change the position of the button. """
        self.pos = pos
        self.text.set_pos(pos+pg.Vector2(10, 10))

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def get_size(self):
        return self.size


class UserParam(UIElement):
    def __init__(self, pos: pg.Vector2, param_name: str, model_param=True, value=None):
        """
        A Tweakable object.
        :param pos: His position
        :param param_name: An identifiant used to recognize him. Please use different names for each UserParam
        :param model_param: a boolean, set to true if the value of the user parameter is used as a parameter for the
        next instantiation of the user's model.
        :param value: The starting value
        """
        super().__init__(pos)
        self.name = param_name
        self.value = value
        self.model_param = model_param


class Slider(UserParam):
    CIRCLE_RADIUS = 5
    BAR_HEIGHT = 2

    def __init__(self, pos: pg.Vector2, length: int, t: str, param_name: str, model_param=True, value=None, min=0,
                 max=10, step=0.01):
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
        if value is None: value = (min + max) / 2
        super().__init__(pos, param_name, model_param, value)
        self.selectedPosX = 0
        self.step = step
        self.min = min
        self.max = max
        self.length = length
        self.set_value(value)
        self.min_image = Text(self.pos, str(self.min), 15)
        self.max_image = Text(self.pos+pg.Vector2(self.length, 0), str(self.max), 15)
        self.max_image.set_pos(self.max_image.pos - pg.Vector2(self.max_image.image.get_width(), 0))
        self.hover = False
        self.type = t

    def draw(self, screen: pg.Surface) -> None:
        if not self.visible:
            return
        pg.draw.rect(screen, (0, 50, 255), pg.Rect(self.pos - pg.Vector2(0, self.BAR_HEIGHT//2),
                                                   pg.Vector2(self.length, self.BAR_HEIGHT)))
        circle_color = (0, 150, 255) if self.hover else (0, 50, 255)
        pg.draw.circle(screen, circle_color, pg.Vector2(self.selectedPosX, self.pos.y), self.CIRCLE_RADIUS)
        if self.hover:
            font = pg.font.Font('freesansbold.ttf', 15)
            if self.type == "SliderInt":
                text = str(self.value)
            else:
                text = f"{self.value:.{self.compute_precision()}f}"
            image = font.render(text, False, (255, 255, 255), (0, 0, 0, 125))
            screen.blit(image, pg.Vector2(self.selectedPosX-image.get_width()/2,
                                          self.pos.y-self.CIRCLE_RADIUS-image.get_height()))
        self.min_image.draw(screen)
        self.max_image.draw(screen)

    def compute_precision(self) -> int:
        return int(max(-log10(self.max - self.min) + 2, 1))

    def set_value(self, value: pg.Vector2):
        value = min(max(value, self.min), self.max)
        self.selectedPosX = (value - self.min) / (self.max - self.min) * self.length + self.pos.x
        self.value = value


class Checkbox(UserParam):
    SIZE = pg.Vector2(20, 20)
    WIDTH = 2

    def __init__(self, pos: pg.Vector2, param_name: str, model_param=True, value=None, *args, **kwargs):
        """
        The class handle the logic for drawing a check box.

        :param pos: The top left corner position
        :param param_name: The name (an identification to recognize it)
        :param model_param: Set to True if it is used a parameter to put for the re-instantiation of the user's Model.
        :param value: The default value.
        :param args: They will be ignored
        :param kwargs: Thy will be ignored
        """
        if len(args) != 0 or len(kwargs) != 0: print(f"Warning: some the arguments have been ignored")
        super().__init__(pos, param_name, model_param, value)

    def draw(self, screen: pg.Surface):
        if not self.visible:
            return
        pg.draw.rect(screen, (0, 0, 0), pg.Rect(self.pos, self.SIZE), width=self.WIDTH)
        if self.value:
            size = pg.Vector2(self.SIZE.x-self.WIDTH, self.SIZE.y-self.WIDTH)
            pg.draw.line(screen, (0, 0, 0), self.pos, self.pos + size, Checkbox.WIDTH)
            pg.draw.line(screen, (0, 0, 0),
                         self.pos+pg.Vector2(size.x, 0),
                         self.pos + pg.Vector2(0, size.y), Checkbox.WIDTH)

    def switch(self):
        self.value = not self.value
