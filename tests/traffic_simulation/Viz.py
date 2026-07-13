from mesa.visualization import SpaceRenderer, SolaraViz
from mesa.visualization.components import AgentPortrayalStyle

from Agent import *
from Model import Model

from mesa_graphics import MesaGraphics, make_plot_component

model = Model(n=40, size=100)
SolaraViz()

def agent_portrayal(agent):
    if isinstance(agent, Obstacle):
        return AgentPortrayalStyle(marker="s", color="red", size=200)
    elif isinstance(agent, Car):
        markers = {
            (1, 0): ">",
            (0, 1): "^",
            (0, -1): "v"
        }
        return AgentPortrayalStyle(marker=markers[tuple(agent.direction)], color=f"C{agent.num}")


renderer = SpaceRenderer(model=model, backend="matplotlib")
renderer.setup_agents(agent_portrayal)
renderer.render()

turn_time_composant = make_plot_component("turn time")

model_params = {
    "n": {
        "type": "SliderInt",
        "value": 40,
        "label": "number of cars",
        "min": 1,
        "max": 50
    },
    "size": {
        "type": "SliderInt",
        "value": 100,
        "label": "size of the grid",
        "min": 20,
        "max": 200
    },
    "configuration": {
        "type": "SliderInt",
        "value": 1,
        "label": "configuration",
        "min": 1,
        "max": 2
    }
}

page = MesaGraphics(
    model,
    renderer,
    model_params=model_params,
    components=[turn_time_composant]
)
