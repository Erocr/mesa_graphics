import os
import time

from mesa.visualization import SpaceRenderer
from mesa.visualization.components import AgentPortrayalStyle, PropertyLayerStyle

from Agent import *
from Model import Model

from mesa_graphics import MesaGraphics, make_plot_component

model = Model(nb_cars=1, nb_passengers=1, width=30)


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
        col = "red"
        if agent.state == Car.IDLE:
            col = "red"
        elif agent.state == Car.SENT_PROPOSITION:
            col = "yellow"
        elif agent.state == Car.PROPOSITION_ACCEPTED:
            col = "orange"
        elif agent.state == Car.TRANSPORTING:
            col = "blue"
        return AgentPortrayalStyle(marker=markers[tuple(agent.direction)], color=col)
    elif isinstance(agent, Passenger):
        return AgentPortrayalStyle(marker="o", color="blue", size=5)


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
average_speed_composant = make_plot_component("average speed", page=1)
nb_static_cars_comp = make_plot_component("nb static cars", page=1)

roads = os.listdir("roads")  # Obtient la liste des fichiers dans le dossier roads
roads = [road[:-5] for road in roads]  # Enlève .json à la fin du nom du fichier

# Les paramètres pour re-instancier le modèle
model_params = {
    "nb_cars": {
        "type": "SliderInt",
        "value": 1,
        "label": "number of cars",
        "min": 1,
        "max": 50
    },
    "nb_passengers": {
        "type": "SliderInt",
        "value": 1,
        "label": "number of passengers",
        "min": 1,
        "max": 50
    },
    "max_speed": {
        "type": "SliderInt",
        "value": 5,
        "label": "max speed",
        "min": 1,
        "max": 10
    }
}

page = MesaGraphics(
    model,
    renderer,
    model_params=model_params,
    components=[average_speed_composant, nb_static_cars_comp]
)
