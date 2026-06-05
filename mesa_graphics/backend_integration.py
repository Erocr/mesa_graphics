import matplotlib.backends.backend_agg as agg
import pygame as pg


def FigureMatplotlib(fig):
    surf = mpl_plot_to_pg_surf(fig)
    return surf


def mpl_plot_to_pg_surf(fig):
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_argb()
    size = canvas.get_width_height()
    return pg.image.fromstring(raw_data, size, "ARGB")

