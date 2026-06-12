import logging

import matplotlib.pyplot as plt
from deffuant_weisbuch.model import DeffuantWeisbuchModel
from mesa_graphics.MesaGraphics import MesaGraphics
from mesa_graphics.matplotlib_components import make_plot_component
from mesa_graphics.backend_integration import FigureMatplotlib
from mesa.visualization.utils import update_counter

# Logging Configuration
logging.basicConfig(level=logging.INFO)

# Expose Model Parameters to the UI
model_params = {
    "rng": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "n": {
        "type": "SliderInt",
        "value": 20,
        "label": "Number of agents:",
        "min": 10,
        "max": 100,
        "step": 1,
        # "description": "Choose how many agents to include in the model"
    },
    "epsilon": {
        "type": "SliderFloat",
        "value": 0.2,
        "label": "Confidence Threshold (ε)",
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
        # "description": "Choose how close should the opinion values be that is required for two agents to interact"
    },
    "mu": {
        "type": "SliderFloat",
        "value": 0.5,
        "label": "Convergence Rate (μ)",
        "min": 0.01,
        "max": 0.5,
        "step": 0.01,
        # "description": "Choose how much should two interacting agents update their opinion values towards each other"
    },
}

# Initial Model Instance
model = DeffuantWeisbuchModel(100, 0.2, 0.5)
renderer = None


def AgentTrajectoriesPlot(model):
    # Trigger rerender whenever model advances
    df = model.datacollector.get_agent_vars_dataframe()

    # Handle case where no data has been collected yet
    if df.empty:
        fig, ax = plt.subplots()
        ax.set_title("No agent data yet")
        return FigureMatplotlib(fig)

    # Reshape data: rows = time, columns = agents
    opinions = df["opinion"].unstack("AgentID")

    fig = plt.Figure((7, 6))
    ax = fig.add_subplot()
    for agent_id in opinions.columns:
        ax.plot(
            opinions.index,
            opinions[agent_id],
            linewidth=1.0,
            alpha=0.8,
        )

    ax.set_xlabel("Time step")
    ax.set_ylabel("Opinion")
    ax.set_title("Opinion Trajectories")
    ax.set_ylim(-1.05, 1.05)
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

    return FigureMatplotlib(fig)


# Visualization Components

OpinionTrajectoryPlot = AgentTrajectoriesPlot
VariancePlot = make_plot_component("Variance")
AcceptanceRatePlot = make_plot_component("Acceptance Rate")
ClusterCountPlot = make_plot_component("Cluster Count")

# Create the SolaraViz page. This will automatically create a server and display
# the visualization elements in a web browser.
#
# Display it using the following command in the example directory:
#   solara run app.py
# It will automatically update and display any changes made to this file.

page = MesaGraphics(
    model,
    renderer=None,
    components=[
        OpinionTrajectoryPlot,
        VariancePlot,
        AcceptanceRatePlot,
        ClusterCountPlot,
    ],
    model_params=model_params,
    name="Deffuant-Weisbuch Model",
)
