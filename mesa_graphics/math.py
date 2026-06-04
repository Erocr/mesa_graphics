import pygame as pg


def ratio_to_px(vector, screen):
    a, b = screen.get_size()
    return pg.Vector2(vector.x * a, vector.y * b)

