from typing import Iterable
from Messaging import Message, Messaging

import mesa


class CellInfo:
    def __init__(self, cell, is_free, directions=None):
        self.cell = cell
        self.is_free = is_free
        if directions is None:
            self.directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        else:
            self.directions = directions

    def __str__(self):
        return str((self.cell.position, self.is_free, self.directions))

    def __repr__(self):
        return str(self)


class MessageReceiver(mesa.discrete_space.CellAgent):
    """
    C'est un agent qui peut recevoir des messages.
    Il doit implémenter la méthode notify qui permet de recevoir un message.
    Par défaut, il ignore tous les messages reçus.
    """
    def notify(self, message: Message):
        pass


class Car(MessageReceiver):
    """An agent with fixed initial wealth."""
    NUM_CAR = 0
    MAX_SPEED = 5
    MAX_SPEED_TURNING = 2

    def __init__(self, model, cell, messaging: Messaging, max_speed=5):
        Car.MAX_SPEED = max_speed
        super().__init__(model)
        self.pos_counter = 0
        self.speed = 0
        self.cell = cell
        self.direction = self.starting_direction()
        self.num = Car.NUM_CAR
        Car.NUM_CAR += 1

        # Garde en mémoire la messagerie pour pouvoir envoyer des messages.
        self.messaging = messaging
        messaging.add_receiver(self)

        # Le chemin est sous la forme d'une chaîne de caractères où chaque caractère indique une direction
        # f pour forward, r pour right et l pour left
        self.path = ""
        self.follow_path = True  # à True pour le test

    def starting_direction(self):
        """
        Calcule la direction initiale de la voiture.
        La direction initiale est une direction au hasard parmi les directions acceptées par sa case.
        """
        possibles = self.model.accepted_directions(self.cell)
        if possibles is None:
            return 1, 0
        return self.random.choice(possibles)

    def step(self):
        perception = self.perceive()
        action = self.deliberate(perception)
        self.do(action)

    def perceive(self) -> list[CellInfo]:
        """
        Perçois le monde.

        Renvoie la case de devant et les cases sur le côté dans l'ordre : [gauche, devant, droite].
        Renvoie des CellInfo correspondant aux cases.
        """
        directions = [self.left_dir(), self.direction, self.right_dir()]
        positions = [(self.cell.position[0]+d[0], self.cell.position[1]+d[1]) for d in directions]
        res = []

        for j in range(3):
            # La position dans la grille complète associée à la position (i, j) de la grille partielle
            cell = self.model.grid.find_nearest_cell(positions[j])
            is_free = self.model.is_free(cell)
            accepted_dirs = self.model.accepted_directions(cell)
            res.append(CellInfo(cell, is_free, accepted_dirs))

        return res

    def left_dir(self):
        """ La direction tournée de 90° vers la gauche """
        return -self.direction[1], self.direction[0]

    def right_dir(self):
        """ La direction tournée de 90° vers la droite """
        return self.direction[1], -self.direction[0]

    def deliberate(self, perception: list[CellInfo]) -> tuple[int, int]:
        """
        Donne la meilleure direction vers laquelle il peut aller.

        :param perception: Les cases où il pourra potentiellement aller, avec plusieurs attributs associés à la case
        :return: le vecteur de mouvement sur la grille
        """
        if self.follow_path:
            return self.deliberation_with_path(perception)
        else:
            return self.deliberation_without_path(perception)

    def deliberation_without_path(self, perception):
        """
        Donne la meilleure direction vers laquelle il peut aller, et si plusieurs ont le même score,
        il en donne une au hasard
        """
        # Commence par calculer les endroits où il pourrait aller si son compteur arrive à MAX_SPEED
        direction = 0, 0
        if self.can_go(self.direction, perception[1]):  # S'il peut aller tout droit
            direction = self.direction

        else:  # Ne peut pas aller tout droit, il peut tourner ou piler
            possible_dirs = []
            if self.can_go(self.left_dir(), perception[0]):  # S'il peut tourner à gauche
                possible_dirs.append(self.left_dir())
            if self.can_go(self.right_dir(), perception[2]):  # S'il peut tourner à droite
                possible_dirs.append(self.right_dir())

            if len(possible_dirs) > 0:  # S'il peut tourner à droite ou à gauche
                direction = self.random.choice(possible_dirs)

        return direction

    def deliberation_with_path(self, perception):
        """ Donne la direction de son chemin s'il peut y aller, sinon il renvoie (0, 0) """
        # Si son chemin est vide, n'avance pas
        if len(self.path) == 0:
            return 0, 0

        # S'il doit aller à gauche, et qu'il peut aller à gauche
        if self.path[0] == "l" and self.can_go(self.left_dir(), perception[0]):
            return self.left_dir()

        # S'il doit aller tout droit, et qu'il peut aller tout droit
        elif self.path[0] == "f" and self.can_go(self.direction, perception[1]):
            return self.direction

        # S'il doit aller à droite, et qu'il peut aller à droite
        elif self.path[0] == "r" and self.can_go(self.right_dir(), perception[2]):
            return self.right_dir()

        # S'il ne peut pas aller là où il doit aller
        else:
            return 0, 0

    def increment_speed(self):
        self.speed = min(self.speed + 1, Car.MAX_SPEED)

    def can_go(self, direction: tuple[int, int], cellInfo: CellInfo):
        return cellInfo.is_free and direction in cellInfo.directions

    def do(self, direction: tuple[int, int]) -> None:
        """
        """
        if direction == (0, 0):  # S'il n'avance pas
            self.speed = 0  # Pile
        elif direction == self.direction:  # S'il va tout droit
            self.increment_speed()  # Accélère
        else:  # S'il tourne
            self.speed = min(self.speed + 1, Car.MAX_SPEED_TURNING)

        # Incrémente le compteur
        self.pos_counter += self.speed
        if self.pos_counter >= Car.MAX_SPEED:
            self.pos_counter -= Car.MAX_SPEED
            if direction != (0, 0):
                self.direction = direction  # Tourne la voiture

            # Avance la voiture
            position = self.cell.position[0] + direction[0], self.cell.position[1] + direction[1]
            self.move_to(self.model.grid.find_nearest_cell(position))

            # S'il suit son chemin, met à jour son chemin
            if self.follow_path:
                self.path = self.path[1:]


class TrafficLight(mesa.discrete_space.CellAgent):
    def __init__(self, model, cell, time=5, states=None, colors=None):
        assert states is not None and len(states) > 0, \
            "Les feu de signalisation (traffic light) doivent avoir un paramètre states non vide"
        assert colors is None or len(states) == len(colors), \
            "Le nombre de couleurs du feu de signalisation doit correspondre au nombre d'états"
        super().__init__(model)
        self.cell = cell
        self.counter_time = 0
        self.states = states
        self.state_index = 0

        # self.state_duration est la durée de chaque état
        if isinstance(time, Iterable):
            self.state_duration = time
        else:
            self.state_duration = [time for _ in range(len(states))]

        # self.colors est la couleur pour chaque état
        self.colors = colors
        if colors is None:
            if len(self.states) == 2:
                self.colors = ["green", "red"]
            elif len(self.states) == 3:
                self.colors = ["green", "orange", "red"]
            elif len(self.states) == 4:
                self.colors = ["green", "orange", "red", "orange"]
            else:
                self.colors = [f"C{i}" for i in range(len(self.states))]

        # Modifie les directions acceptées dans la case du feu avec celles de son état initial
        self.model.modify_directions(self.cell, self.states[self.state_index])

    def step(self):
        self.counter_time += 1
        if self.counter_time >= self.state_duration[self.state_index]:
            self.counter_time -= self.state_duration[self.state_index]

            self.state_index = (self.state_index + 1) % len(self.states)
            self.model.modify_directions(self.cell, self.states[self.state_index])


class Passenger(MessageReceiver):
    """ Le passager est un agent qui va demander aux voitures de le transporter à son but. """
    def __init__(self, model, cell, messaging: Messaging, goal):
        super().__init__(model)
        self.cell = cell
        self.goal = goal
        self.transporting_car = None

        # Garde en mémoire la messagerie pour pouvoir envoyer des messages.
        self.messaging = messaging
        messaging.add_receiver(self)

    def transport(self, car):
        self.transporting_car = car
