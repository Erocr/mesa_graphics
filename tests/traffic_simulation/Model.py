import mesa
import numpy as np
from mesa.discrete_space import PropertyLayer
import json

from Agent import Car


def average_speed(model):
    speeds = [agent.speed for agent in model.agents if isinstance(agent, Car)]
    return sum(speeds) / len(speeds)


class Model(mesa.Model):
    def __init__(self, n=1, size=10, max_speed=5, seed=None, file_name: str = "one_way_road"):
        super().__init__(seed=seed)
        self.num_agents = n
        self.datacollector = mesa.DataCollector(model_reporters={"average speed": average_speed})
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
                                                                 random=self.random, capacity=1)

        # Calcule les positions où les voitures peuvent aller
        self.free_pos = []
        for cell in self.grid.all_cells.cells:
            i, j = cell.position
            typ = self.tile_type(_grid, _tile_types, width, (int(i), int(j)))
            if typ["road"]:
                self.free_pos.append(cell)
            if "directions" in typ:
                directions_map = {"up": (0, 1), "down": (0, -1), "right": (1, 0), "left": (-1, 0)}
                self._accepted_directions[cell] = []
                for direction in typ["directions"]:
                    self._accepted_directions[cell].append(directions_map[direction])

    def tile_type(self, _grid, tile_types, width, pos):
        x, y = pos
        x %= width
        if x > len(_grid[y]):
            return {"road": False}
        typ = str(_grid[y][x])
        if typ in tile_types:
            return tile_types[typ]
        else:
            return {"road": False}

    def accepted_directions(self, cell):
        # Par défaut toutes les directions sont autorisées.
        return self._accepted_directions.get(cell, None)

    def is_road(self, cell):
        return cell in self.free_pos

    def is_free(self, cell: mesa.discrete_space.Cell):
        return self.is_road(cell) and cell.is_empty

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")

