import matplotlib.backends.backend_agg as agg
import pygame as pg


def FigureMatplotlib(fig):
    """ Transforms a matplotlib figure into a pygame.Surface. It has the same name of the Solara version to
    help switching between the two visualizations. """
    surf = mpl_plot_to_pg_surf(fig)
    return surf


def mpl_plot_to_pg_surf(fig):
    """ Transforms a matplotlib figure into a pygame.Surface. """
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_argb()
    size = canvas.get_width_height()
    return pg.image.fromstring(raw_data, size, "ARGB")

