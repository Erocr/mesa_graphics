import pygame as pg
from mesa_graphics.Card import Card


class View:
    def __init__(self):
        pg.font.init()
        self.screen = pg.display.set_mode((1000, 700), pg.RESIZABLE)
        self.pages = {
            0: Card(pg.Vector2(0.34, 0), pg.Vector2(0.66, 1), self.screen)
        }
        self.ui_card = self.create_ui_card()
        self.page = 0

    def create_ui_card(self):
        result = Card(pg.Vector2(0, 0), pg.Vector2(0.33, 1), self.screen)
        result.add_text(pg.Vector2(0.1, 0), pg.Vector2(0.8, 0.2), "test")
        return result

    def draw(self):
        self.ui_card.draw()
        self.pages[self.page].draw()

        pg.display.flip()
