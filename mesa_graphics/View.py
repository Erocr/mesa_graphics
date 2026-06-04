import pygame as pg


class View:
    def __init__(self):
        self.window = pg.display.set_mode((500, 500))

    def draw(self):
        pg.display.flip()
