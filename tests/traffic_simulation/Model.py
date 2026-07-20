import mesa
import numpy as np
from mesa.discrete_space import PropertyLayer
import json

from Agent import Car, TrafficLight


def average_speed(model):
    speeds = [agent.speed for agent in model.agents if isinstance(agent, Car)]
    return sum(speeds) / len(speeds)


def number_static_cars(model):
    res = 0
    for agent in model.agents:
        if isinstance(agent, Car) and agent.speed == 0:
            res += 1
    return res


class Model(mesa.Model):
    def __init__(self, n=1, size=10, max_speed=5, seed=None, file_name: str = "one_way_road"):
        super().__init__(seed=seed)
        self.num_agents = n
        self.datacollector = mesa.DataCollector(model_reporters={"average speed": average_speed,
                                                                 "nb static cars": number_static_cars})
        self.length = size
        self.free_pos: list[mesa.discrete_space.Cell] = []  # Les positions où les voitures peuvent aller
        self._accepted_directions = {}  # Associe aux cellules une liste des directions acceptées, par défaut toutes
        # les directions sont acceptées
        self.grid: mesa.discrete_space.OrthogonalVonNeumannGrid = None  # noqa

        if file_name[-5:] != ".json": file_name = file_name + ".json"
        self.import_road(file_name)

        Car.create_agents(self, n, [self.free_pos[i] for i in range(n)], max_speed=max_speed)

        blocked_layer = PropertyLayer(
            "blocked", (self.grid.width, self.grid.height), default_value=0, dtype=int
        )
        blocked_layer.data = np.ones((self.grid.width, self.grid.height))
        for c in self.free_pos:
            blocked_layer.data[int(c.position[0])][int(c.position[1])] = 0
        self.grid.add_property_layer(blocked_layer)

        self.datacollector.collect(self)

    def import_road(self, file_name):
        # Open file, and load the content
        with open(file_name, "r") as file:
            file_content = file.read()
        content = json.loads(file_content)

        # Prends les types de tiles définies dans le fichier, par défault il n'y en a pas
        _tile_types = {}
        if "tile_types" in content:
            _tile_types = content["tile_types"]

        # Prends la grille et calcule la taille
        _grid = content["grid"]
        height = len(_grid)
        width = max(len(line) for line in _grid)

        # Crée la grille
        self.grid = mesa.discrete_space.OrthogonalVonNeumannGrid((self.length, height), torus=True,
                                                                 random=self.random)

        # Calcule les positions où les voitures peuvent aller
        self.free_pos = []
        for cell in self.grid.all_cells.cells:
            i, j = cell.position
            j = self.grid.height - 1 - j  # Retourne verticalement, car le fichier json donne la grille dans le mauvais sens
            typ = self.tile_type(_grid, _tile_types, width, (int(i), int(j)))
            if typ["road"]:
                self.free_pos.append(cell)
            if "directions" in typ:
                self._accepted_directions[cell] = self.direction_names_to_vectors(typ["directions"])
            if "traffic light" in typ:  # Must be a dictionary
                parameters = typ["traffic light"]
                TrafficLight.create_agents(self, 1, [cell], time=parameters.get("time", 5),
                                           states=parameters.get("states", None))

    def direction_names_to_vectors(self, directions):
        directions_map = {"up": (0, 1), "down": (0, -1), "right": (1, 0), "left": (-1, 0)}
        res = []
        for direction in directions:
            res.append(directions_map[direction])
        return res

    def tile_type(self, _grid, tile_types, width, pos):
        x, y = pos
        x %= width
        if x >= len(_grid[y]):
            return {"road": False}
        typ = str(_grid[y][x])
        if typ in tile_types:
            return tile_types[typ]
        else:
            return {"road": False}

    def accepted_directions(self, cell):
        # Par défaut toutes les directions sont autorisées.
        return self._accepted_directions.get(cell, None)

    def modify_directions(self, cell, directions):
        # Appelé par le feu tricolore
        self._accepted_directions[cell] = self.direction_names_to_vectors(directions)

    def is_road(self, cell):
        return cell in self.free_pos

    def is_free(self, cell: mesa.discrete_space.Cell):
        for agent in cell.agents:
            if isinstance(agent, Car):
                return False
        return self.is_road(cell)

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")

