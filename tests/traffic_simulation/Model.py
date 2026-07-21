import mesa
import numpy as np
from mesa.discrete_space import PropertyLayer
import json

from Agent import Car, TrafficLight


def average_speed(model):
    """ La vitesse moyenne des voitures """
    velocities = [agent.speed for agent in model.agents if isinstance(agent, Car)]
    return sum(velocities) / len(velocities)


def number_static_cars(model):
    """ Le nombre de voitures qui ont pilé, et qui ne peuvent pas bouger"""
    res = 0
    for agent in model.agents:
        if isinstance(agent, Car) and agent.speed == 0:
            res += 1
    return res


class Model(mesa.Model):
    def __init__(self, n=1, width=10, max_speed=5, seed=None, file_name: str = "one_way_road"):
        super().__init__(seed=seed)
        self.datacollector = mesa.DataCollector(model_reporters={"average speed": average_speed,
                                                                 "nb static cars": number_static_cars})

        self.free_pos: list[mesa.discrete_space.Cell] = []  # Les positions où les voitures peuvent aller
        self._accepted_directions = {}  # Associe aux cellules une liste des directions acceptées, par défaut toutes
        # les directions sont acceptées
        self.grid: mesa.discrete_space.OrthogonalVonNeumannGrid = None  # noqa  Mets la grille à None, elle sera créée
        # dans import_road

        # Importe le fichier avec la grille
        if file_name[-5:] != ".json": file_name = file_name + ".json"
        self.import_road(file_name, width)

        # Crée les agents dans les endroits qui sont libres selon le fichier qui a été importé
        Car.create_agents(self, n, [self.free_pos[i] for i in range(n)], max_speed=max_speed)

        # Crée un layer pour pouvoir afficher les cases en bleues lorsqu'elles sont accessibles, et en rouge
        # lorsqu'elles ne le sont pas
        # On met dans blocked_layer.data 1 pour rouge et 0 pour bleu
        blocked_layer = PropertyLayer(
            "blocked", (self.grid.width, self.grid.height), default_value=1, dtype=int
        )
        blocked_layer.data = np.ones((self.grid.width, self.grid.height))
        for c in self.free_pos:
            blocked_layer.data[int(c.position[0])][int(c.position[1])] = 0
        self.grid.add_property_layer(blocked_layer)

    def import_road(self, file_name, width):
        """ Crée la grille, et rempli la grille selon comment il a été décrit dans le fichier file_name """
        # Ouvre le fichier, et charge le contenu
        with open(file_name, "r") as file:
            file_content = file.read()
        content = json.loads(file_content)

        # Prends les types de tiles définies dans le fichier, par défault il n'y en a pas
        _tile_types = {}
        if "tile_types" in content:
            _tile_types = content["tile_types"]

        # Prends la grille et calcule la taille
        _grid = content["grid"]
        grid_height = len(_grid)
        grid_width = max(len(line) for line in _grid)

        # Crée la grille
        self.grid = mesa.discrete_space.OrthogonalVonNeumannGrid((width, grid_height), torus=True,
                                                                 random=self.random)

        # Calcule les positions où les voitures peuvent aller
        self.free_pos = []
        for cell in self.grid.all_cells.cells:
            i, j = cell.position

            # Retourne verticalement, car matplotlib affiche la grille à l'envers
            j = self.grid.height - 1 - j

            # Applique les paramètres associés à la tuile
            typ = self.tile_type(_grid, _tile_types, grid_width, (int(i), int(j)))
            if typ["road"]:
                self.free_pos.append(cell)
            if "directions" in typ:
                self._accepted_directions[cell] = self._direction_names_to_vectors(typ["directions"])
            if "traffic light" in typ:  # typ["traffic light"] est censé être un dictionnaire
                parameters = typ["traffic light"]
                TrafficLight.create_agents(self, 1, [cell], time=parameters.get("time", 5),
                                           states=parameters.get("states", None))

    def tile_type(self, _grid, tile_types, width, pos):
        """ Extrait les paramètres de la tuile
        _grid est la grille des avec les id des types de tuiles
        tile_types est le dictionnaire qui associe l'id du type avec ses paramètres
        width est la largeur de la grille
        pos est la position de la tuile dont on souhaite connaître les paramètres
        """
        x, y = pos
        x %= width  # Si la longueur de la route est plus grande que celle dans le json, la grille est répétée

        # Si une ligne est moins longue que les autres, alors elle est remplie par des blocs inpraticables
        if x >= len(_grid[y]):
            return {"road": False}

        # Retrouve le paramètre associé au numéro dans la grille
        typ = str(_grid[y][x])  # On doit faire str(...) car le type est défini comme une string au dans le json
        if typ in tile_types:
            return tile_types[typ]
        else:
            return {"road": False}

    def accepted_directions(self, cell: mesa.discrete_space.Cell):
        """
        Les directions acceptées pour cette cellule.
        La voiture doit arriver sur cette case avec une de ces directions.
        """
        # Par défaut toutes les directions sont autorisées.
        return self._accepted_directions.get(cell, None)

    def modify_directions(self, cell: mesa.discrete_space.Cell, directions: list[tuple[int, int]]):
        """ Modifie les directions acceptées par la cellule cell """
        # Appelé par le feu tricolore
        self._accepted_directions[cell] = self._direction_names_to_vectors(directions)

    def is_road(self, cell: mesa.discrete_space.Cell):
        """ Renvoie si c'est une case de route """
        return cell in self.free_pos

    def is_free(self, cell: mesa.discrete_space.Cell):
        """ If a car can go on this cell """
        for agent in cell.agents:
            if isinstance(agent, Car):
                return False
        return self.is_road(cell)

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")

    def _direction_names_to_vectors(self, directions):
        """
        Transforme une liste de directions up/right/down/left en une liste de directions sous forme de vecteurs
        (0, 1)/(1, 0)/(0, -1)/(-1, 0)
        """
        directions_map = {"up": (0, 1), "down": (0, -1), "right": (1, 0), "left": (-1, 0)}
        res = []
        for direction in directions:
            res.append(directions_map[direction])
        return res

