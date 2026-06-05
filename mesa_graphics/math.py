import pygame as pg


def mul(v1, v2):
    return pg.Vector2(v1.x * v2.x, v1.y * v2.y)


def div(v1, v2):
    return pg.Vector2(v1.x / v2.x, v1.y / v2.y)


def add(v, e):
    return pg.Vector2(v.x + e, v.y + e)


def sub(v, e):
    return add(v, -e)



