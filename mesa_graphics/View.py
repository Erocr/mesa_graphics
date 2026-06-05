import pygame as pg
from mesa_graphics.Card import Card
from mesa_graphics.BoundingElement import ScreenBounds


class View:
    def __init__(self):
        pg.font.init()
        self.screen = pg.display.set_mode((1000, 700), pg.RESIZABLE)
        self.screen_bounds = ScreenBounds(self.screen)
        self.pages = {
            0: Card(self.screen_bounds, pg.Vector2(0.34, 0), pg.Vector2(0.66, 1))
        }
        self.ui_card = self.create_ui_card()
        self.page = 0

    def create_ui_card(self):
        result = Card(self.screen_bounds, pg.Vector2(0, 0), pg.Vector2(0.33, 1))
        result.add_text(pg.Vector2(0.1, 0), pg.Vector2(0.8, 0.1), "test")
        return result

    def draw(self):
        self.ui_card.draw(self.screen)
        self.pages[self.page].draw(self.screen)

        pg.display.flip()
