import mesa
from matplotlib.figure import Figure
from mesa_graphics import MesaGraphics, make_plot_component, make_space_component, FigureMatplotlib
# Import the local MoneyModel.py
from voiture import *


# dessiner une voiture rouge
def agent_portrayal(agent):
    size = 10
    color = "tab:red"

    if agent.vitesse > 0:
        size = 50
        color = "tab:blue"
    return {"size": size, "color": color}


def Histogram(model):
    fig = Figure()
    ax = fig.subplots()
    speed_vals = [agent.vitesse for agent in model.agents]
    # Note: you have to use Matplotlib's OOP API instead of plt.hist
    # because plt.hist is not thread-safe.
    ax.hist(speed_vals, bins=10)
    return FigureMatplotlib(fig)


model_params = {
    "N": {
        "type": "SliderInt",
        "value": 1,
        "label": "Number of agents:",
        "min": 1,
        "max": 10,
        "step": 1,
    },
    "VMAX":{
        "type": "SliderInt",
        "value": 5,
        "label": "Maximum speed:",
        "min": 1,
        "max": 10,
        "step": 1,
    }
}

# Create initial model instance
model1 = Route(N=1, taille=20)

SpaceGraph = make_space_component(agent_portrayal)

RunPlot = make_plot_component("average_speed_run")

#Create the Dashboard
page = MesaGraphics(
    model1,
    components=[SpaceGraph, RunPlot, Histogram],
    model_params=model_params,
    name="Simulation de Voiture",
)
