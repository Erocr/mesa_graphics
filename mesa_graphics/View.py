import pygame as pg
from mesa_graphics.Card import Card


class View:
    def __init__(self):
        self.screen = pg.display.set_mode((1000, 700), pg.RESIZABLE)
        self.pages = {
            0: Card(pg.Vector2(0.34, 0), pg.Vector2(0.66, 1))
        }
        self.ui_card = Card(pg.Vector2(0, 0), pg.Vector2(0.33, 1))
        self.page = 0

    def draw(self):
        self.ui_card.draw(self.screen)
        self.pages[self.page].draw(self.screen)

        pg.display.flip()
