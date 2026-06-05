from collections.abc import Callable
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from mesa_graphics.backend_integration import FigureMatplotlib


def make_mpl_plot_component(
    measure: str | dict[str, str] | list[str] | tuple[str],
    post_process: Callable | None = None,
    page: int = 0,
    save_format="png",
):
    """Create a plotting function for a specified measure.

    Args:
        measure (str | dict[str, str] | list[str] | tuple[str]): Measure(s) to plot.
        post_process: a user-specified callable to do post-processing called with the Axes instance.
        page: Page number where the plot should be displayed.
        save_format: save format of figure in solara backend

    Returns:
        (function, page): A tuple of a function that creates a PlotMatplotlib component and a page number.
    """

    def MakePlotMatplotlib(model):
        return PlotMatplotlib(model, measure, post_process=post_process)

    return MakePlotMatplotlib, page


def PlotMatplotlib(
    model,
    measure,
    post_process: Callable | None = None
):
    """Create a Matplotlib-based plot for a measure or measures.

    Args:
        model (mesa.Model): The model instance.
        measure (str | dict[str, str] | list[str] | tuple[str]): Measure(s) to plot.
        dependencies (list[any] | None): Optional dependencies for the plot.
        post_process: a user-specified callable to do post-processing called with the Axes instance.
        save_format: format used for saving the figure.

    Returns:
        solara.FigureMatplotlib: A component for rendering the plot.
    """
    fig = Figure()
    ax = fig.subplots()
    df = model.datacollector.get_model_vars_dataframe()
    if isinstance(measure, str):
        ax.plot(df.loc[:, measure])
        ax.set_ylabel(measure)
    elif isinstance(measure, dict):
        for m, color in measure.items():
            ax.plot(df.loc[:, m], label=m, color=color)
        ax.legend(loc="best")
    elif isinstance(measure, list | tuple):
        for m in measure:
            ax.plot(df.loc[:, m], label=m)
        ax.legend(loc="best")

    if post_process is not None:
        post_process(ax)

    ax.set_xlabel("Step")
    # Set integer x axis
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    return FigureMatplotlib(fig)
