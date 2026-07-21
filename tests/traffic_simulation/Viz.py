from mesa.visualization import SpaceRenderer, SolaraViz
from mesa.visualization.components import AgentPortrayalStyle, PropertyLayerStyle

from Agent import *
from Model import Model

from mesa_graphics import MesaGraphics, make_plot_component

model = Model(n=10, width=20)
SolaraViz()


def agent_portrayal(agent):
    """
    Indique comment afficher les voitures et les feux de signalisation dans la grille.
    """
    if isinstance(agent, Car):
        markers = {
            (1, 0): ">",
            (0, 1): "^",
            (0, -1): "v",
            (-1, 0): "<"
        }
        return AgentPortrayalStyle(marker=markers[tuple(agent.direction)], color=f"C{agent.num}")
    if isinstance(agent, TrafficLight):
        col = 'red' if agent.state_index == 0 else "blue"
        return AgentPortrayalStyle(marker="o", color=col, alpha=0.5)


def propertylayer_portrayal(layer):
    """
    Indique comment afficher les cases dans la grille.
    En bleu si c'est de la route, et en rouge sinon.
    """
    if layer.name == "blocked":
        return PropertyLayerStyle(colormap="coolwarm",
                                  alpha=0.5,
                                  colorbar=False,
                                  vmin=0,
                                  vmax=1)


# La grille
renderer = SpaceRenderer(model=model, backend="matplotlib")
renderer.setup_agents(agent_portrayal)
renderer.setup_propertylayer(propertylayer_portrayal)
renderer.render()

# Les plots en dessous de la grille
average_speed_composant = make_plot_component("average speed")
nb_static_cars_comp = make_plot_component("nb static cars")

# Les paramètres pour re-instancier le modèle
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
    "width": {
        "type": "SliderInt",
        "value": 20,
        "label": "length of the route",
        "min": 5,
        "max": 50
    },
    "file_name": {
        "type": "InputText",
        "value": "one_way_road",
        "label": "map"
    }
}

page = MesaGraphics(
    model,
    renderer,
    model_params=model_params,
    components=[average_speed_composant, nb_static_cars_comp]
)
