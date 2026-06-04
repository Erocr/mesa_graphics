import pygame as pg


def ratio_to_px(vector, sized_object):
    a, b = sized_object.get_size()
    return pg.Vector2(vector.x * a, vector.y * b)


def px_to_ratio(vector, sized_object):
    a, b = sized_object.get_size()
    return pg.Vector2(vector.x / a, vector.y / b)

