from typing import Iterable

import mesa
import numpy as np
from mesa.discrete_space import PropertyLayer
import json
from Messaging import BROAD_CAST, CARS, PASSENGERS
from Agent import Passenger, MessageReceiver
from BasicCar import BasicCar
from a_star_algorithm import cost_delta

# Il suffit de changer cette ligne de code pour changer le type de voiture qu'on utilise
Car = BasicCar


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


def number_passengers(model):
    return len([agent for agent in model.agents if isinstance(agent, Passenger)])


class Model(mesa.Model):
    def __init__(self, nb_cars=1, nb_passengers=1, width=30, max_speed=5, seed=None, file_name: str = "city",
                 time_recompute_path=3, time_before_accept=3, time_passenger_spawn=-1, custom_entities=None):
        """
        :param nb_cars: Le nombre de voitures
        :param nb_passengers: Le nombre de passagers au début de la simulation
        :param width: La largeur de la carte (n'est pas utile dans cette version)
        :param max_speed: La vitesse maximale des agents.
        Plus elle est élevée, plus les agents prennent du temps pour arriver à leur vitesse maximale.
        :param seed:
        :param file_name: Le fichier qui décrit la carte
        :param time_recompute_path: Le temps qu'attendent les voitures avant de recalculer le chemin
        :param time_before_accept: Le temps qu'attendent les passagers avant d'accepter une voiture
        :param time_passenger_spawn: Le temps avant qu'un passager apparaîsse
        :param custom_entities: Des entités qui apparaissent au début, choisies par l'utilisateur
        """

        super().__init__(seed=seed)
        self.datacollector = mesa.DataCollector(model_reporters={"average speed": average_speed,
                                                                 "nb static cars": number_static_cars,
                                                                 "passengers": number_passengers})

        # La discussion number le plus grand trouvé dans les dicussions.
        # C'est utile pour créer des nouvelles discussions.
        self.max_discussion_nb = 0

        # Change les paramètres des agents en fonction de ce qui a été entré par l'utilisateur
        Car.TIME_BEFORE_RECOMPUTING_PATH = time_recompute_path
        Passenger.TIME_WAIT_BEFORE_ACCEPT = time_before_accept
        self.time_passenger_spawn = time_passenger_spawn
        self.time = 0

        self.free_pos: list[mesa.discrete_space.Cell] = []  # Les positions où les voitures peuvent aller
        self._accepted_directions = {}  # Associe aux cellules une liste des directions acceptées, par défaut toutes
        # les directions sont acceptées
        self.grid: mesa.discrete_space.OrthogonalVonNeumannGrid = None  # noqa  Mets la grille à None, elle sera créée
        # dans import_road

        # Importe le fichier avec la grille
        if file_name[-5:] != ".json": file_name = file_name + ".json"
        self.import_road(file_name, width)

        # Crée les agents dans les endroits qui sont libres selon le fichier qui a été importé
        free_pos = self.free_pos.copy()
        self.random.shuffle(free_pos)
        Car.create_agents(self, nb_cars, [free_pos[i] for i in range(nb_cars)], max_speed=max_speed)

        for _ in range(nb_passengers):
            self.spawn_passenger()

        if custom_entities is not None:
            for entity in custom_entities:
                if entity[0] == Car:
                    Car.create_agents(self, 1, entity[1], max_speed=max_speed)
                elif entity[1] == Passenger:
                    Passenger.create_agents(self, 1, entity[1], entity[2])

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
        with open("roads/"+file_name, "r") as file:
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
        self.grid = mesa.discrete_space.OrthogonalVonNeumannGrid((width, grid_height), random=self.random)

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

        self.remove_blocking_directions()

    def remove_blocking_directions(self):
        # La liste des directions à enlever
        # De la forme [(cell1, direction1), ...]
        to_remove = []

        # Tant qu'il y a des éléments à enlever, continue.
        # Peut-être qu'enlever une direction va rendre une autre case bloquée.
        while True:
            # Regarde pour chaque cellule, chaque direction, et elève celles qui sont bloquées
            for cell in self.grid.all_cells:
                if not self.is_road(cell):
                    continue

                for direction in self.accepted_directions(cell):

                    # Calcule si une voiture dans la cellule `cell`, et avec la direction `direction` est bloquée
                    blocked = True
                    for neighbor in cell.neighborhood:
                        # cost_delta est une fonction qui renvoie -1 si la voiture ne peut pas y aller,
                        # et une heuristique de coût si elle peut y aller
                        if cost_delta(cell, neighbor, direction, self) > 0:
                            blocked = False

                    # Si la case est bloquée, on l'ajoute dans les éléments à enlever
                    if blocked:
                        to_remove.append((cell, direction))

            # S'il n'y a plus rien à enlever, s'arrête
            if len(to_remove) == 0:
                return

            # Pour chaque élément à enlever, on l'enlève
            for cell, direction in to_remove:
                if cell in self._accepted_directions:
                    self._accepted_directions[cell].remove(direction)
                else:
                    self._accepted_directions[cell] = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    self._accepted_directions[cell].remove(direction)

            to_remove = []

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
        return self._accepted_directions.get(cell, [(0, 1), (1, 0), (-1, 0), (0, -1)])

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

    def blocking(self, cell):
        """
        Renvoie si une voiture bloque la cellule
        None si personne ne bloque
        """
        for agent in cell.agents:
            if isinstance(agent, Car):
                return agent

    def send_msg(self, message, sender, who=BROAD_CAST):
        self.max_discussion_nb = max(message.discussion_nb, self.max_discussion_nb)
        receivers = []
        if who == BROAD_CAST:
            receivers = self.agents
        elif who == CARS:
            receivers = [agent for agent in self.agents if isinstance(agent, Car)]
        elif who == PASSENGERS:
            receivers = [agent for agent in self.agents if isinstance(agent, Passenger)]
        elif isinstance(who, MessageReceiver):
            receivers = [who]
        elif isinstance(who, Iterable):
            receivers = who

        for receiver in receivers:
            receiver.notify(message, sender)

    def spawn_passenger(self):
        cell1 = self.random.choice(self.free_pos)
        cell2 = self.random.choice(self.free_pos)
        Passenger.create_agents(self, 1, cell1, cell2)

    def step(self):
        self.time += 1
        if self.time_passenger_spawn >= 0 and self.time % self.time_passenger_spawn == 0:
            self.spawn_passenger()
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

