from mesa.visualization import SpaceRenderer, SolaraViz
from mesa.visualization.components import AgentPortrayalStyle, PropertyLayerStyle

from Agent import *
from Model import Model

from mesa_graphics import MesaGraphics, make_plot_component

model = Model(n=10, size=40)
SolaraViz()


def agent_portrayal(agent):
    if isinstance(agent, Obstacle):
        return AgentPortrayalStyle(size=0, alpha=0)
    elif isinstance(agent, Car):
        markers = {
            (1, 0): ">",
            (0, 1): "^",
            (0, -1): "v"
        }
        return AgentPortrayalStyle(marker=markers[tuple(agent.direction)], color=f"C{agent.num}")


def propertylayer_portrayal(layer):
    if layer.name == "blocked":
        return PropertyLayerStyle(colormap="coolwarm",
                                  alpha=0.5,
                                  colorbar=False,
                                  vmin=0,
                                  vmax=1)


renderer = SpaceRenderer(model=model, backend="matplotlib")
renderer.setup_agents(agent_portrayal)
renderer.setup_propertylayer(propertylayer_portrayal)
renderer.render()

turn_time_composant = make_plot_component("average turn time")
average_speed_composant = make_plot_component("average speed")

model_params = {
    "n": {
        "type": "SliderInt",
        "value": 10,
        "label": "number of cars",
        "min": 1,
        "max": 50
    },
    "max_speed": {
        "type": "SliderInt",
        "value": 5,
        "label": "max speed",
        "min": 1,
        "max": 10
    },
    "size": {
        "type": "SliderInt",
        "value": 40,
        "label": "length of the route",
        "min": 20,
        "max": 100
    },
    "configuration": {
        "type": "SliderInt",
        "value": 1,
        "label": "configuration",
        "min": 1,
        "max": 3
    }
}

page = MesaGraphics(
    model,
    renderer,
    model_params=model_params,
    components=[turn_time_composant, average_speed_composant]
)
