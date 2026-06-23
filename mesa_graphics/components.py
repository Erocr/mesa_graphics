import itertools
import warnings
from collections.abc import Callable

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from mesa.visualization.mpl_space_drawing import draw_space

from .backend_integration import FigureMatplotlib


def make_mpl_plot_component(
        measure: str | dict[str, str] | list[str] | tuple[str],
        post_process: Callable | None = None,
        page: int = 0
):
    """Create a plotting function for a specified measure using matplotlib backend.

    :param measure: measure (str | dict[str, str] | list[str] | tuple[str]): Measure(s) to plot.
    :param post_process: a user-specified callable to do post-processing called with the Axes instance.
    :param page: Page number where the plot should be displayed.

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

    :param model: (mesa.Model) The model instance.
    :param measure: (str | dict[str, str] | list[str] | tuple[str]) Measure(s) to plot.
    :param post_process: a user-specified callable to do post-processing called with the Axes instance.

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


def create_space_component(renderer):
    """Create a space visualization component for the given renderer. Must not be used by user. """

    def SpaceVisualizationComponent(model):
        """Component that renders the model's space using the provided renderer."""
        return SpaceRendererComponent(model, renderer)

    return SpaceVisualizationComponent


def SpaceRendererComponent(
        model,
        renderer
):
    """Render the space of a model using a SpaceRenderer.


    :param model: (Model) The model whose space is to be rendered.
    :param renderer: A SpaceRenderer instance to render the model's space.
    """
    # update renderer's space according to the model's space/grid
    renderer.space = getattr(model, "grid", getattr(model, "space", None))

    if renderer.backend == "matplotlib":
        # Clear the previous plotted data and agents
        all_artists = [
            renderer.canvas.lines[:],
            renderer.canvas.collections[:],
            renderer.canvas.patches[:],
            renderer.canvas.images[:],
            renderer.canvas.artists[:],
        ]

        # Remove duplicate colorbars from the canvas
        for cbar in renderer.backend_renderer._active_colorbars:
            cbar.remove()
        renderer.backend_renderer._active_colorbars.clear()

        # Chain them together into a single iterable
        for artist in itertools.chain.from_iterable(all_artists):
            artist.remove()

        if renderer.space_mesh:
            renderer.draw_structure()
        if renderer.agent_mesh:
            renderer.draw_agents()
        if renderer.propertylayer_mesh:
            renderer.draw_propertylayer()

        if renderer.post_process and not renderer._post_process_applied:
            renderer.post_process(renderer.canvas)
            renderer._post_process_applied = True

        return FigureMatplotlib(renderer.canvas.get_figure())
    else:
        assert False, "Only the matplotlib backend has been implemented yet"
        structure = renderer.space_mesh if renderer.space_mesh else None
        agents = renderer.agent_mesh if renderer.agent_mesh else None
        propertylayer = renderer.propertylayer_mesh or None

        if renderer.space_mesh:
            structure = renderer.draw_structure()
        if renderer.agent_mesh:
            agents = renderer.draw_agents()
        if renderer.propertylayer_mesh:
            propertylayer = renderer.draw_propertylayer()

        spatial_charts_list = [
            chart for chart in [structure, propertylayer, agents] if chart
        ]

        final_chart = None
        if spatial_charts_list:
            final_chart = (
                spatial_charts_list[0]
                if len(spatial_charts_list) == 1
                else alt.layer(*spatial_charts_list).resolve_axis(
                    x="independent", y="independent"
                )
            )

        if final_chart is None:
            # If no charts are available, return an empty chart
            final_chart = (
                alt.Chart(pd.DataFrame()).mark_point().properties(width=450, height=350)
            )

        if renderer.post_process:
            final_chart = renderer.post_process(final_chart)

        final_chart = final_chart.configure_view(stroke="black", strokeWidth=1.5)

        solara.FigureAltair(final_chart, on_click=None, on_hover=None)
        return None


make_plot_component = make_mpl_plot_component


def make_space_matplotlib(*args, **kwargs):  # noqa: D103
    warnings.warn(
        "make_space_matplotlib has been renamed to make_mpl_space_component",
        FutureWarning,
        stacklevel=2,
    )
    return make_mpl_space_component(*args, **kwargs)


def make_mpl_space_component(
        agent_portrayal: Callable | None = None,
        propertylayer_portrayal: dict | None = None,
        post_process: Callable | None = None,
        **space_drawing_kwargs):
    """Create a Matplotlib-based space visualization component.

    :param agent_portrayal: Function to portray agents.
    :param propertylayer_portrayal: Dictionary of PropertyLayer portrayal specifications
    :param post_process: a callable that will be called with the Axes instance. Allows for fine tuning plots (e.g., control ticks)
    :param space_drawing_kwargs: additional keyword arguments to be passed on to the underlying space drawer function. See
                               the functions for drawing the various spaces for further details.

    ``agent_portrayal`` is called with an agent and should return a dict. Valid fields in this dict are "color",
    "size", "marker", "zorder", alpha, linewidths, and edgecolors. Other field are ignored and will result in a user warning.

    Returns:
        function: A function that creates a SpaceMatplotlib component
    """
    if agent_portrayal is None:
        def agent_portrayal(a):
            return {}

    def MakeSpaceMatplotlib(model):
        return SpaceMatplotlib(
            model,
            agent_portrayal,
            propertylayer_portrayal,
            post_process=post_process,
            **space_drawing_kwargs,
        )

    return MakeSpaceMatplotlib


def SpaceMatplotlib(
        model,
        agent_portrayal,
        propertylayer_portrayal,
        post_process: Callable | None = None,
        **space_drawing_kwargs,
):
    """Create a Matplotlib-based space visualization component."""

    space = getattr(model, "grid", None)
    if space is None:
        space = getattr(model, "space", None)

    fig = Figure()
    ax = fig.add_subplot()

    draw_space(
        space,
        agent_portrayal,
        propertylayer_portrayal=propertylayer_portrayal,
        ax=ax,
        **space_drawing_kwargs,
    )

    if post_process is not None:
        post_process(ax)

    return FigureMatplotlib(fig)


make_space_component = make_mpl_space_component
