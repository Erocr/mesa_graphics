import pygame as pg


class View:
    def __init__(self, model):
        pg.font.init()
        self.screen = pg.display.set_mode((1000, 700), pg.RESIZABLE)
        self.model = model

    def draw(self):
        self.screen.fill((255, 255, 255))

        pg.display.flip()
