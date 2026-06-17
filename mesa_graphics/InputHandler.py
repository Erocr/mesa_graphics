import pygame as pg


class Key:
    def __init__(self, d=0):
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
    """
    This class simplify the pygame inputs and make them more accessible via preprocessing them
    You can access inputs via the methods pressed(), holding() and released()
    """
    def __init__(self):
        self.keys = {}
        self._pg_events()
        self.events = {}
        self.quit = False
        self._mouse_pos = pg.Vector2(0, 0)
        self._scroll_direction = pg.Vector2(0, 0)

    def _pg_events(self):
        """ Associate in `self.keys` the pygame keys constants to a string describing the key """
        pg_keys = pg.__dict__
        for p in pg_keys:
            if p[:2] == "K_":
                self.keys[p[2:]] = pg_keys[p]
        self.keys["mouse_left"] = -1
        self.keys["mouse_right"] = -3

    def update_counters(self):
        keys = list(self.events.keys())
        for evt in keys:
            if self.events[evt].duration < 0:
                self.events.pop(evt)
            else:
                self.events[evt].duration += 1

    def update(self):
        """
        Analyse the new events sent by pygame, and write them in a more understandable way
        This method shall be called once per frame
        """
        self._mouse_pos = pg.Vector2(*pg.mouse.get_pos())
        self._scroll_direction = pg.Vector2(0, 0)

        for evt in pg.event.get():
            if evt.type == pg.KEYDOWN:
                self.events[evt.key] = Key()
            elif evt.type == pg.KEYUP:
                self.events[evt.key].duration = -1 - (self.events[evt.key].duration > 0)
            elif evt.type == pg.QUIT:
                self.quit = True
            elif evt.type == pg.MOUSEBUTTONDOWN:
                self.events[-evt.button] = Key()
            elif evt.type == pg.MOUSEBUTTONUP:
                self.events.pop(-evt.button)
            if evt.type == pg.MOUSEWHEEL:
                self._scroll_direction = pg.Vector2(evt.x, evt.y)

    def key_id(self, key):
        """
        This function generalizes the pygame keys. Moreover, it gives a better error if it doesn't exist.
        :param key: the pygame key or the string describing the key.
        :return: the pygame key associated.
        """
        if isinstance(key, int):
            return key
        elif key in self.keys:
            return self.keys[key]
        elif key[2:] in self.keys:
            return self.keys[key[2:]]
        else:
            raise Exception(f"key {key} does not exist")

    def pressed(self, key):
        """ Returns True only during the frame in which the user presse the key. """
        key = self.key_id(key)
        return key in self.events and self.events[key].pressed

    def holding(self, key):
        """ Returns True while the user is pressing the key. """
        key = self.key_id(key)
        return key in self.events and self.events[key].holding

    def released(self, key):
        """ Returns True only during the frame in which the user release the key. """
        key = self.key_id(key)
        return key in self.events and self.events[key].released

    @property
    def mouse_pos(self):
        """ Get the mouse position. """
        return self._mouse_pos

    @property
    def scroll_direction(self):
        """ Get the vector representing how much the user is scrolling """
        return self._scroll_direction
