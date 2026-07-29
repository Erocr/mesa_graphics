from typing import Iterable
from Messaging import Message, Messaging
import heapq  # J'utilise les tas pour l'algorithme A*
from a_star_algorithm import a_star

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
    def notify(self, message: Message, sender):
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
        self.sent_proposition = None  # Le passager à qui il a proposé de le transporter
        self.discussion_nb = None  # Le numéro de discussion avec le passager
        self.route_computed = ""  # La route pour aller jusqu'au passager à qui il a proposé

        self.transport = None  # The passenger he transports

        # Le chemin est sous la forme d'une chaîne de caractères où chaque caractère indique une direction
        # f pour forward, r pour right et l pour left
        self.path = ""
        self.follow_path = True

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
        if self.sent_proposition is not None and self.sent_proposition.cell == self.cell:
            self.transport = self.sent_proposition
            self.sent_proposition = None
            self.transport.transported_by(self)
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

            # S'il suit un chemin, met à jour son chemin
            if self.follow_path:
                self.path = self.path[1:]

            # S'il a un passager, bouge le passager
            if self.transport is not None:
                self.transport.move_to(self.cell)

    def notify(self, message: Message, sender):
        if message.performatif == Message.REQUEST:
            if message.content[:9] == "passenger" and self.sent_proposition is None and self.transport is None:
                splitted = message.content.split(" ")
                pos = int(splitted[1]), int(splitted[2])
                self.route_computed = a_star(self.cell, self.model.grid.find_nearest_cell(pos), self.direction, self.model)
                self.messaging.notify(Message(Message.INFORMATIF, f"distance {len(self.route_computed)}",
                                              message.discussion_nb), self)
                self.sent_proposition = sender
                self.discussion_nb = message.discussion_nb

        elif message.performatif == Message.INFORMATIF:
            if message.content == "ok" and sender == self.sent_proposition and message.discussion_nb == self.discussion_nb:
                self.path = self.route_computed
                self.follow_path = True
            elif message.content == "no" and sender == self.sent_proposition and message.discussion_nb == self.discussion_nb:
                self.sent_proposition = None
                self.route_computed = ""
            elif message.content[:9] == "direction" and message.discussion_nb == self.discussion_nb and sender == self.transport:
                splitted = message.content.split(" ")
                pos = int(splitted[1]), int(splitted[2])
                self.path = a_star(self.cell, self.model.grid.find_nearest_cell(pos), self.direction, self.model)
                self.follow_path = True
            elif message.content == "disappear":
                if self.transport == sender:
                    self.transport = None
                if self.sent_proposition == sender:
                    self.sent_proposition = None


class Passenger(MessageReceiver):
    TIME_WAIT_BEFORE_ACCEPT = 3

    """ Le passager est un agent qui va demander aux voitures de le transporter à son but. """
    def __init__(self, model, cell, messaging: Messaging, goal_cell: mesa.discrete_space.Cell):
        super().__init__(model)
        self.cell = cell
        self.goal = goal_cell
        self.transporting_car = None

        self.discussion_nb = 0  # Son nombre de discussions, utile pour savoir si c'est bien à lui qu'on parle,
        # ou à un autre passager
        self.min_distance = None  # La distance minimale parmi les distances que lui ont envoyées les taxis
        self.best_taxi = None  # Le meilleur taxi jusque-là
        self.has_taxi = False  # S'il a accepté un taxi
        self.taxis = []  # Tous les taxis qui lui ont proposé de le transporter

        # Garde en mémoire la messagerie pour pouvoir envoyer des messages.
        self.messaging = messaging
        messaging.add_receiver(self)

        self.send_time = 0
        self.send_position()

    def notify(self, message: Message, sender):
        if message.performatif == Message.INFORMATIF and message.discussion_nb == self.discussion_nb:
            if message.content[:8] == "distance":
                distance = int(message.content.split(" ")[1])
                if self.min_distance is None or distance < self.min_distance:
                    self.min_distance = distance
                    self.best_taxi = sender
                self.taxis.append(sender)

    def transported_by(self, car):
        self.transporting_car = car
        self.messaging.notify_specific(Message(Message.INFORMATIF,
                                               f"direction {int(self.goal.position[0])} {int(self.goal.position[1])}",
                                               self.discussion_nb), self, car)

    def step(self):
        # S'il est dans une voiture, il n'a rien à faire
        if self.transporting_car is not None:
            # C'est à la voiture de le déplacer quand elle se déplace

            if self.cell == self.goal:
                self.disappear()

        self.send_time += 1  # Le temps depuis qu'il a envoyé le message augmente
        if self.send_time >= self.TIME_WAIT_BEFORE_ACCEPT:
            self.accept_taxi()
            if not self.has_taxi:
                self.send_position()
                print("proposition from "+str(self.cell.position))

    def send_position(self):
        """ Envoie sa position à tous les taxis """
        self.send_time = 0  # Depuis quand est-ce qu'il a demandé aux taxis de venir
        self.discussion_nb = self.messaging.get_new_discussion_nb()
        self.messaging.notify(Message(Message.REQUEST,
                                      f"passenger {int(self.cell.position[0])} {int(self.cell.position[1])}",
                                      discussion_nb=self.discussion_nb),
                              self)

    def accept_taxi(self):
        """
        Envoie un message à tous les taxis qui lui ont répondu.
        - 'ok' si c'est le meilleur taxi.
        - 'no' s'il y a un meilleur taxi.

        Si aucun taxi ne lui a répondu, la fonction ne fait rien
        """
        for taxi in self.taxis:
            # Si c'est le meilleur taxi, envoie 'ok'
            if taxi == self.best_taxi:
                self.messaging.notify_specific(Message(Message.INFORMATIF, "ok", self.discussion_nb),
                                               self,
                                               taxi)

            # Si ce n'est pas le meilleur taxi, envoie 'no'
            else:
                self.messaging.notify_specific(Message(Message.INFORMATIF, "no", self.discussion_nb),
                                               self,
                                               taxi)
        self.taxis = []
        if self.best_taxi is not None:
            self.has_taxi = True
        self.best_taxi = None  # Only for test

    def disappear(self):
        self.messaging.notify(Message(Message.INFORMATIF, "disappear"), self)
        self.cell.remove_agent(self)
        self.model.agents.remove(self)
