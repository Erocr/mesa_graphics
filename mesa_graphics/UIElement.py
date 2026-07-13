from pathlib import Path
from typing import Callable
from math import log10

import pygame as pg


DARK1_BLUE = (12, 60, 180)
BLUE = (24, 118, 210)
LIGHT1_BLUE = (100, 150, 255)
LIGHT2_BLUE = (120, 180, 255)
LIGHT2_GRAY = (230, 230, 230)
LIGHT1_GRAY = (190, 190, 190)
GRAY = (125, 125, 125)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def mul(v1: pg.Vector2, v2: pg.Vector2):
    return pg.Vector2(v1.x * v2.x, v1.y * v2.y)


class UIElement:
    def __init__(self, pos: pg.Vector2, visible=True):
        """ It is an abstract class describing an element of UI. """
        self.pos = pos
        self._visible = visible

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, vis):
        self._visible = vis

    def draw(self, screen: pg.Surface):
        """ This function draws the UIElement onto the screen. """
        assert False, "this is an abstract method"

    def set_pos(self, new_pos):
        self.pos = new_pos


class Rectangle(UIElement):
    def __init__(self, pos: pg.Vector2, size: pg.Vector2, color, *args, **kwargs):
        """
        :param pos: The top-left corner position. It must be a pg.Vector2.
        :param size: The size of the rectangle. It must be a pg.Vector2.
        :param color: The filling color. It is an index in the palette.
        :param args: Arguments to add in the pg.draw.rect function
        :param kwargs: Arguments to add in the pg.draw.rect function
        """
        super().__init__(pos)
        self.size = size
        self.color = color
        self.args = args
        self.kwargs = kwargs

    def draw(self, screen: pg.Surface):
        pg.draw.rect(screen, self.color, pg.Rect(self.pos, self.size), *self.args, **self.kwargs)


class ShadowedCard(UIElement):
    def __init__(self, in_position: pg.Vector2, in_size: pg.Vector2, color_in, width: int = 5, *args, **kwargs):
        super().__init__(in_position)
        start_col = pg.Vector3(100, 100, 100)
        end_col = pg.Vector3(*LIGHT2_GRAY)
        self.rects = []
        for i in range(width):
            I = pg.Vector2(i, i)
            color = start_col + (end_col - start_col) * i / width
            self.rects.append(Rectangle(in_position-I+pg.Vector2(3, 3), in_size + 2*I - pg.Vector2(3, 3), color, width=2, *args, **kwargs))
        self.rects.insert(0, Rectangle(in_position, in_size, color_in, *args, **kwargs))

    def draw(self, screen: pg.Surface):
        for rect in self.rects:
            rect.draw(screen)
        self.rects[0].draw(screen)

    def set_size(self, new_in_size):
        for i in range(1, len(self.rects)):
            rect = self.rects[i]
            rect.size = new_in_size + 2 * pg.Vector2(i) - pg.Vector2(3)
        self.rects[0].size = new_in_size

    def set_pos(self, pos):
        v = pos - self.pos
        for rect in self.rects:
            rect.set_pos(rect.pos + v)


class Shadow(UIElement):
    def __init__(self, p1, p2, direction, length, initial_color=(125, 125, 125), final_color=(255, 255, 255),
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

    def set_pos(self, new_pos):
        v = self.p2 - self.p1
        self.p1 = new_pos
        self.p2 = new_pos + v


class Text(UIElement):
    def __init__(self, pos: pg.Vector2, text: str, font: pg.font.Font, color=(0, 0, 0), ratio=pg.Vector2(1, 1)):
        """
        :param pos: The top-left corner position. It must be a pg.Vector2
        :param text: The string shown
        :param font: The font
        """
        super().__init__(pos)
        self.font = font
        self.image = font.render(text, True, color)

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.pos)

    def set_pos(self, pos: pg.Vector2):
        self.pos = pos


class Button(UIElement):
    alreadyUsed = set()

    def __init__(self, pos, text: str, font, name=None, custom_draw: Callable = None, font_color=WHITE):
        """
        The logic for drawing a clickable button.

        :param pos: The top-left corner position. It must be a pg.Vector2.
        :param text: The string shown in the button.
        :param font: The font of the text in the button.
        :param name: An identification. It is used to associate actions in the Controller.
        :param custom_draw: A function that take the button and the screen, and draw the button on the screen.
        If no name is given, the name is the text. If the name is already used, it will put a number
        right after it.
        """
        super().__init__(pos)
        self.font = font
        self.text = Text(pos+pg.Vector2(10, 10), text, font, color=font_color)
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
        self.ratio = pg.Vector2(1, 1)

    def draw(self, screen: pg.Surface):
        if self.custom_draw:
            self.custom_draw(self, screen)
        else:
            bg_color = LIGHT1_BLUE if self.hover else BLUE
            if self.locked:
                bg_color = WHITE
            pg.draw.rect(screen, bg_color, pg.Rect(self.pos, self.size), border_radius=8)
            self.text.draw(screen)

    def modify_text(self, new_text: str, font=None, color=(0, 0, 0)):
        """
        Modifies the text written in the button.
        :param new_text: the new string to show.
        :param font: The new font. If you don't put the font size, it will put the previous font
        :param color: The color of the new text, black by default
        """
        if font is None:
            font = self.font
        else:
            self.font = font
        self.text = Text(self.pos + pg.Vector2(10, 10), new_text, font, color=color)
        self.size.x = self.text.image.get_width() + 20

    def set_pos(self, pos: pg.Vector2):
        """ Change the position of the button. """
        self.pos = pos
        self.text.set_pos(pos+mul(pg.Vector2(10, 10), self.ratio))

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def get_size(self):
        return self.size


class UserParam(UIElement):
    def __init__(self, pos: pg.Vector2, param_name: str, model_param=True, associated_method=None, value=None):
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
        self.associated_method = associated_method


class Slider(UserParam):
    CIRCLE_RADIUS = 5
    BAR_HEIGHT = 2
    FONT = None

    def __init__(self, pos: pg.Vector2, t: str, param_name: str, model_param=True, associated_method=None,
                 value=None, min=0, max=10, step=0.01):
        """
        This class handle the logic for drawing a slider.

        :param t: The type of the slider, it can be "SliderInt" or "SliderFloat"
        :param pos: A pg.Vector2 describing the left position of the slider.
        :param value: The initial value. If None, value is initialized with the middle value.
        :param min: The minimum value it can take.
        :param max: The maximum value it can take.
        :param step: The step between two possible values.
        """
        if Slider.FONT is None:
            path = pg.font.get_default_font()
            Slider.FONT = pg.font.Font(path, 10)
        assert min <= max, "min shall be less than max"
        assert t in ("SliderInt", "SliderFloat"), f"type {t} is unknown"
        if value is None: value = (min + max) / 2
        super().__init__(pos, param_name, model_param, associated_method, value)
        self.selectedPosX = 0
        self.step = step
        self.min = min
        self.max = max
        self.length = 270 - pos.x
        self.set_value(value)
        self.hover = False
        self.type = t

    def draw(self, screen: pg.Surface) -> None:
        pg.draw.rect(screen, BLUE, pg.Rect(self.pos + pg.Vector2(0, -self.BAR_HEIGHT//2),
                                                   pg.Vector2(self.selectedPosX-self.pos.x, self.BAR_HEIGHT)))
        pg.draw.rect(screen, (180, 180, 180), pg.Rect(self.pos + pg.Vector2(self.selectedPosX-self.pos.x, -self.BAR_HEIGHT // 2),
                                                      pg.Vector2(self.length-self.selectedPosX+self.pos.x, self.BAR_HEIGHT)))
        circle_color = (0, 150, 255) if self.hover else BLUE
        pg.draw.circle(screen, circle_color, pg.Vector2(self.selectedPosX, self.pos.y), self.CIRCLE_RADIUS)
        if self.hover:
            font = pg.font.Font('freesansbold.ttf', 15)
            if self.type == "SliderInt":
                text = str(self.value)
            else:
                text = f"{self.value:.{self.compute_precision()}f}"
            image = font.render(text, True, (255, 255, 255), (0, 0, 0, 125))
            screen.blit(image, pg.Vector2(self.selectedPosX-image.get_width()/2,
                                          self.pos.y-self.CIRCLE_RADIUS-image.get_height()))

    def secondary_draw(self, screen):
        pass

    def set_pos(self, new_pos):
        self.pos = new_pos

    def compute_precision(self) -> int:
        return int(max(-log10(self.max - self.min) + 2, 1))

    def set_value(self, value: pg.Vector2):
        value = min(max(value, self.min), self.max)
        self.selectedPosX = (value - self.min) / (self.max - self.min) * self.length + self.pos.x
        self.value = value


class Checkbox(UserParam):
    WIDTH = 2
    SIZE = pg.Vector2(20, 20)

    def __init__(self, pos: pg.Vector2, param_name: str, model_param=True, associated_method=None, value=None, *args, **kwargs):
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
        super().__init__(pos, param_name, model_param, associated_method, value)
        self.size = pg.Vector2(20, 20)

    def draw(self, screen: pg.Surface):
        pg.draw.rect(screen, color=0, rect=pg.Rect(self.pos, self.size), width=self.WIDTH)
        if self.value:
            size = pg.Vector2(self.size.x-self.WIDTH, self.size.y-self.WIDTH)
            pg.draw.line(screen, (0, 0, 0), self.pos, self.pos + size, Checkbox.WIDTH)
            pg.draw.line(screen, (0, 0, 0),
                         self.pos+pg.Vector2(size.x, 0),
                         self.pos + pg.Vector2(0, size.y), Checkbox.WIDTH)

    def switch(self):
        self.value = not self.value


class Select(UserParam):
    def __init__(self, pos: pg.Vector2, param_name: str, model_param=True, associated_method=None, value=None, values=None, *args, **kwargs):
        """
        This class handle the logic to draw a selection between different values.

        :param pos: The position on the screen (top left)
        :param param_name: The name (an identification to recognize it)
        :param model_param: Set to True if it is used a parameter to put for the re-instantiation of the user's Model.
        :param value: The default value.
        :param values: The different values it can take.
        :param args: They will be ignored
        :param kwargs: Thy will be ignored
        """
        super().__init__(pos, param_name, model_param, associated_method, value)
        if values is None:
            values = [value]
        self.values = values
        assert self.value in self.values, "The default value must be in proposed values"
        self.index_value = self.values.index(value)
        self.is_toggled = False
        default_path = pg.font.get_default_font()
        font = pg.font.Font(default_path, 15)
        self.values_images = []
        self.size = pg.Vector2(270 - self.pos.x, 20)
        self.toggle_size = pg.Vector2(270 - self.pos.x, 30)
        for value in values:
            image = font.render(str(value), True, (0, 0, 0))
            new_size = (min(image.get_width(), self.size.x - 2 * 5),
                        min(image.get_height(), self.size.y))
            _image = pg.Surface(new_size).convert_alpha()
            _image.fill((255, 255, 255, 0))
            _image.blit(image, (0, 0))
            self.values_images.append(_image)
        self.values_images_original = self.values_images.copy()

    def draw(self, screen: pg.Surface):
        rect = pg.Rect(self.pos, self.size)

        # Fond
        pg.draw.rect(screen, WHITE, rect, border_radius=6)

        # Bordure
        pg.draw.rect(screen, (180, 180, 180), rect, width=2, border_radius=6)

        # Image
        screen.blit(self.values_images[self.index_value],
                    self.pos + pg.Vector2(8, 3))

        # Flèche
        cx = self.pos.x + self.size.x - 15
        cy = self.pos.y + self.size.y / 2
        points = [
            (cx - 5, cy - 3),
            (cx, cy + 3),
            (cx + 5, cy - 3)
        ]
        pg.draw.polygon(screen, (90, 90, 90), points)

    def secondary_draw(self, screen: pg.Surface):
        """ The secondary_draw function draws above the other elements. It draws the toggled version. """
        rect = pg.Rect(
            self.pos,
            (self.size.x, self.toggle_size.y * len(self.values))
        )

        # Ombre
        shadow = rect.move(3, 3)
        pg.draw.rect(screen, (180, 180, 180), shadow, border_radius=6)

        # Fond
        pg.draw.rect(screen, WHITE, rect, border_radius=6)

        # Bordure
        pg.draw.rect(screen, (170, 170, 170), rect, width=2, border_radius=6)

        for i, image in enumerate(self.values_images):

            y = i * self.toggle_size.y

            item = pg.Rect(
                self.pos.x + 2,
                self.pos.y + y,
                self.toggle_size.x - 4,
                self.toggle_size.y
            )

            # Valeur sélectionnée
            if i == self.index_value:
                pg.draw.rect(screen, (220, 235, 255), item, border_radius=6)

            # Séparateur
            if i:
                pg.draw.line(screen, (220, 220, 220), (item.left + 5, item.top), (item.right - 5, item.top), 1)
            screen.blit(image, (item.x + 8, item.y + 5))

    def set_value(self, value):
        self.value = value
        self.index_value = self.values.index(value)


class InputText(UserParam):
    def __init__(self, pos: pg.Vector2, param_name: str, model_param=True, associated_method=None, value=None, *args, **kwargs):
        super().__init__(pos, param_name, model_param, associated_method, value)
        if self.value is None: self.value = ""
        self.cursor_pos = len(self.value)
        self.ratio = pg.Vector2(1, 1)
        default_path = pg.font.get_default_font()
        self.size = pg.Vector2(270 - self.pos.x, 20)
        self.font = pg.font.Font(default_path, 15)
        self.text_im = None
        self.compute_text_im()
        self.is_focused = False
        self.gap = 0

    def draw(self, screen):
        rect = pg.Rect(self.pos, self.size)
        # Fond
        pg.draw.rect(screen, WHITE, rect, border_radius=6)

        # Bordure
        pg.draw.rect(screen, (180, 180, 180), rect, width=2, border_radius=6)

        screen.blit(self.text_im, self.pos+pg.Vector2(8, self.size.y/2 - self.text_im.get_height()/2))
        if self.is_focused:
            im = self.font.render(self.value[:self.cursor_pos], True, (0, 0, 0))
            cursor_pos = im.get_width() * self.ratio.x + self.gap
            pg.draw.line(screen, (0, 0, 0), self.pos+pg.Vector2(8+cursor_pos, 3),
                         self.pos+pg.Vector2(8+cursor_pos, self.size.y-4), 3)

    def write(self, letter):
        self.value = self.value[:self.cursor_pos] + letter + self.value[self.cursor_pos:]
        self.move_cursor(1)
        self.compute_text_im()

    def remove(self):
        if self.cursor_pos == 0:
            return
        self.value = self.value[:self.cursor_pos-1] + self.value[self.cursor_pos:]
        self.move_cursor(-1)
        self.compute_text_im()

    def suppr(self):
        if self.cursor_pos == len(self.value):
            return
        self.value = self.value[:self.cursor_pos] + self.value[self.cursor_pos+1:]
        self.compute_text_im()

    def move_cursor(self, amount):
        self.cursor_pos = min(max(self.cursor_pos + amount, 0), len(self.value))
        im = self.font.render(self.value[:self.cursor_pos], True, (0, 0, 0))
        cursor_pos = im.get_width() * self.ratio.x + self.gap
        if cursor_pos > self.size.x - 16:
            self.gap -= cursor_pos - self.size.x + 16
        if cursor_pos < (self.size.x - 16) * 0.2:
            self.gap += (self.size.x - 16) * 0.2 - cursor_pos
            if self.gap > 0: self.gap = 0
        self.compute_text_im()

    def compute_text_im(self):
        self.text_im = self.font.render(self.value, True, (0, 0, 0))
        self.text_im = pg.transform.scale_by(self.text_im, self.ratio)
        if self.text_im.get_width() > self.size.x - 16:
            im = pg.Surface((self.size.x - 16, self.text_im.get_height())).convert_alpha()
            im.fill((0, 0, 0, 0))
            im.blit(self.text_im, (self.gap, 0))
            self.text_im = im

    def secondary_draw(self, screen):
        pass


class ScrollingSlider(UserParam):
    def __init__(self, pos, is_vert, screen_size_y, scrolling_length_y, name=""):
        """

        :param pos: The top left corner position
        :param is_vert: True if the slider is vertical
        :param length: The length in pixel of the slider on the screen.
        :param screen_size_y: The height of the part viewable by the user
        :param scrolling_length_y: The size where the user can scroll
        :param name: An id in order to know where it does scroll

         _____
        |    |<-- screen_size
        |____|
        |    |
        |    |<-- scrolling_length
        |    |
        |____|
        """
        super().__init__(pos, name, False, value=0)
        self.hover = False
        self.is_vert = is_vert
        if is_vert:
            self.size = pg.Vector2(10, screen_size_y)
        else:
            self.size = pg.Vector2(screen_size_y, 10)
        self.name = name
        self.screen_size_y = screen_size_y
        self.scrolling_length_y = scrolling_length_y
        self.pointer_size = pg.Vector2(0)
        self.pointer_length = 0
        self.update_pointer_size()

    def update_pointer_size(self):
        # self.screen_size_y / (self.screen_size_y + self.scrolling_length_y) is between 0 and 1, it is the ratio
        # of the size of the screen.
        # Finally, we multiply by self.screen_size_y which is the size of the scrolling bar.
        self.pointer_length = self.screen_size_y / (self.screen_size_y + self.scrolling_length_y) * self.screen_size_y
        self.pointer_size = pg.Vector2(self.pointer_length)
        if self.is_vert:
            self.pointer_size.x = 6
        else:
            self.pointer_size.y = 6

    def draw(self, screen):
        if self.pointer_length < self.screen_size_y:
            pointer_color = GRAY if self.hover else LIGHT1_GRAY
            pg.draw.rect(screen, WHITE, pg.Rect(self.pos, self.size))
            pg.draw.rect(screen, pointer_color, pg.Rect(self.get_pointer_pos(), self.pointer_size), border_radius=6)

    def get_pointer_pos(self):
        direction = pg.Vector2(0, 1) if self.is_vert else pg.Vector2(1, 0)
        # self.value / self.scrolling_length_y is a ratio between 0 and 1 of how much the user scrolled.
        if self.scrolling_length_y == 0:
            pos = 0
        else:
            pos = self.value / self.scrolling_length_y * (self.screen_size_y - self.pointer_length - 2)
        return self.pos + direction*pos + pg.Vector2(2, 2)

    def update_max_scrolling(self, new_max_scrolling):
        self.scrolling_length_y = new_max_scrolling
        self.update_pointer_size()

    def resize(self, new_screen_size_y):
        self.scrolling_length_y = self.screen_size_y + self.scrolling_length_y - new_screen_size_y
        self.screen_size_y = new_screen_size_y
        self.update_pointer_size()
        if self.is_vert:
            self.size = pg.Vector2(10, self.screen_size_y)
        else:
            self.size = pg.Vector2(self.screen_size_y, 10)

    def move_pointer_pos(self, amount: int | float | pg.Vector2):
        """
        The amount is in pixels, on the slide.

        pos is the position in his axis.
        For example, if it is a vertical slider, his axis is vertical.
        """
        if isinstance(amount, pg.Vector2):
            if self.is_vert: amount = amount.y
            else: amount = amount.x

        self.value += amount / (self.screen_size_y - self.pointer_length - 2) * self.scrolling_length_y
        self.clamp_value()

    def clamp_value(self):
        if self.value < 0: self.value = 0
        if self.value > self.scrolling_length_y: self.value = self.scrolling_length_y

    def is_above_pointer(self, point: pg.Vector2):
        if self.is_vert:
            return point.y < self.get_pointer_pos().y
        else:
            return point.x < self.get_pointer_pos().x
