import matplotlib.backends.backend_agg as agg
import matplotlib.pyplot as plt
import pygame as pg


def FigureMatplotlib(fig: plt.Figure) -> pg.Surface:
    """ Transforms a matplotlib figure into a pygame.Surface. It has the same name of the Solara version to
    help switching between the two visualizations. Be aware that you must use the result of this function. """
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


def FigureText(text: str, font_size=15, font_color=(0, 0, 0), background_color=(255, 255, 255)) -> pg.Surface:
    lines = text.split("\n")
    default_path = pg.font.get_default_font()
    font = pg.font.Font(default_path, font_size)

    images = []
    for line in lines:
        images.append(font.render(line, True, font_color, background_color))

    width = max([image.get_width() for image in images])
    height = sum([image.get_height() for image in images])

    res = pg.Surface((width, height))

    y = 0
    for image in images:
        res.blit(image, (0, y))
        y += image.get_height()
    return res
