import pygame as pg


class Key:
    def __init__(self, d=0):
        # How much since the user is holding the key.
        # If the user just released it, the duration is negative.
        # And if the user is not pressing the key at all, the Key object should not exist.
        self.duration = d

    @property
    def holding(self):
        return self.duration >= 0

    @property
    def pressed(self):
        return self.duration == 0 or self.duration == -1

    @property
    def released(self):
        return self.duration < 0


class InputHandler:
    def __init__(self):
        """
        This class simplifies the pygame inputs and makes them more accessible via preprocessing them
        You can access inputs via the methods pressed(), holding() and released()
        """
        self.keys = {}
        self._pg_events()
        self.events = {}
        self.quit = False
        self._mouse_pos = pg.Vector2(0, 0)
        self._prev_mouse_pos = pg.Vector2(0, 0)
        self._scroll_direction = pg.Vector2(0, 0)
        self.resized = None
        self.unicode = ""

    def _pg_events(self):
        """ Associate in `self.keys` the pygame keys constants to a string describing the key """
        pg_keys = pg.__dict__
        for p in pg_keys:
            if p[:2] == "K_":
                self.keys[p[2:]] = pg_keys[p]
        self.keys["mouse_left"] = self.keys["mouse left"] = -1
        self.keys["mouse_right"] = self.keys["mouse right"] = -3

    def update_counters(self):
        """
        Every key has a counter, counting how many frames were the last modification.
        This function updates this counters.
        """
        keys = list(self.events.keys())
        for evt in keys:
            if self.events[evt].duration < 0:
                self.events.pop(evt)
            else:
                self.events[evt].duration += 1

    def update(self):
        """
        Analyze the new events sent by pygame, and write them in a more understandable way
        This method shall be called once per frame
        """
        self._prev_mouse_pos = self._mouse_pos
        self._mouse_pos = pg.Vector2(*pg.mouse.get_pos())
        self._scroll_direction = pg.Vector2(0, 0)
        self.resized = None
        self.unicode = ""

        for evt in pg.event.get():
            if evt.type == pg.KEYDOWN:  # The user presses a button
                self.events[evt.key] = Key()
                self.unicode += evt.unicode
            elif evt.type == pg.KEYUP:  # The user releases a button
                self.events[evt.key].duration = -1 - (self.events[evt.key].duration > 0)
            elif evt.type == pg.QUIT:  # The user closes the window
                self.quit = True
            elif evt.type == pg.MOUSEBUTTONDOWN:  # The user presses a mouse button
                self.events[-evt.button] = Key()  # The mouse buttons are negative
            elif evt.type == pg.MOUSEBUTTONUP:  # The user releases a mouse button
                self.events.pop(-evt.button)  # The mouse buttons are negative
            elif evt.type == pg.MOUSEWHEEL:  # The user scrolls with the mouse or a touchpad
                self._scroll_direction = pg.Vector2(evt.x, evt.y)
            elif evt.type == pg.VIDEORESIZE:  # The user resizes the window
                self.resized = pg.Vector2(evt.w, evt.h)

    def key_id(self, key: int | str):
        """
        This function generalizes the pygame keys as strings or numbers.
        Moreover, it gives a better error if it doesn't exist.
        :param key: The pygame key or the string describing the key.
        :return: The pygame key associated.
        """
        if isinstance(key, int):
            return key
        elif key in self.keys:
            return self.keys[key]
        elif key[2:] in self.keys:
            return self.keys[key[2:]]
        else:
            raise Exception(f"key {key} does not exist")

    def get_duration(self, key: int | str):
        """ Returns the number of frames since the user started to press the key.
        It returns -1 if this key is not pressed
        """
        key = self.key_id(key)
        if key in self.events:
            return self.events[key].duration
        else:
            return -1

    def resize(self) -> pg.Vector2 | None:
        return self.resized

    def pressed(self, key: int | str):
        """ Returns True only during the frame in which the user presse the key. """
        key = self.key_id(key)
        return key in self.events and self.events[key].pressed

    def holding(self, key: int | str):
        """ Returns True while the user is pressing the key. """
        key = self.key_id(key)
        return key in self.events and self.events[key].holding

    def released(self, key: int | str):
        """ Returns True only during the frame in which the user releases the key. """
        key = self.key_id(key)
        return key in self.events and self.events[key].released

    @property
    def mouse_pos(self):
        """ Get the mouse position. """
        return self._mouse_pos

    @property
    def mouse_movement(self):
        return self._mouse_pos - self._prev_mouse_pos

    @property
    def scroll_direction(self):
        """ Get the vector representing how much the user is scrolling """
        return self._scroll_direction
