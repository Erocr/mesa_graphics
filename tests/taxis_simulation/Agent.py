from Messaging import Message
from a_star_algorithm import a_star

import Messaging
import mesa


class CellInfo:
    def __init__(self, cell, is_road, directions=None, blocking=None):
        self.cell = cell
        self.is_road = is_road
        self.blocking = blocking
        if directions is None:
            self.directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        else:
            self.directions = directions

    def __str__(self):
        return str((self.cell.position, self.is_road, self.directions, self.blocking))

    def __repr__(self):
        return str(self)


class MessageReceiver(mesa.discrete_space.CellAgent):
    """
    C'est un agent qui peut recevoir des messages.
    Il doit implémenter la méthode notify qui permet de recevoir un message.
    Par défaut, il ignore tous les messages reçus.
    """

    def __init__(self, model):
        super().__init__(model)
        self.messages = []

    def notify(self, message: Message, sender):
        self.messages.append((message, sender))


class Passenger(MessageReceiver):
    TIME_WAIT_BEFORE_ACCEPT = 3

    """ Le passager est un agent qui va demander aux voitures de le transporter à son but. """

    def __init__(self, model, cell, goal_cell: mesa.discrete_space.Cell):
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

        self.send_time = Passenger.TIME_WAIT_BEFORE_ACCEPT  # Envoie directement la posiiton aux taxis

    def step(self):
        perception = self.perceive()
        action = self.deliberate(perception)
        self.do(action)

    def perceive(self):
        return self.read_messages()

    def deliberate(self, perception):
        pass

    def do(self, action):
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

        # Si le taxi lui a promis de venir mais ne vient pas, il l'oublie
        if self.has_taxi and self.send_time > 100 and self.transporting_car is None:
            self.send_time = 0
            self.has_taxi = False

    def read_messages(self):
        for i in reversed(range(len(self.messages))):
            message, sender = self.messages[i]

            # Si le message est une proposition d'un taxi en réponse à sa demande
            if message.performatif == Message.INFORMATIF and message.discussion_nb == self.discussion_nb:
                # Cherche la meilleure réponse
                if message.content[:8] == "distance":
                    distance = int(message.content.split(" ")[1])
                    if self.min_distance is None or distance < self.min_distance:
                        self.min_distance = distance
                        self.best_taxi = sender
                    self.taxis.append(sender)

            self.messages.pop(i)

    def transported_by(self, car):
        self.transporting_car = car
        self.model.send_msg(Message(Message.INFORMATIF,
                                    f"direction {int(self.goal.position[0])} {int(self.goal.position[1])}",
                                    self.discussion_nb),
                            self,
                            car)

    def send_position(self):
        """ Envoie sa position à tous les taxis """
        self.send_time = 0  # Depuis quand est-ce qu'il a demandé aux taxis de venir
        self.discussion_nb = self.model.max_discussion_nb + 1
        self.model.send_msg(Message(Message.REQUEST,
                                    f"passenger {int(self.cell.position[0])} {int(self.cell.position[1])} {int(self.goal.position[0])} {int(self.goal.position[1])}",
                                    discussion_nb=self.discussion_nb),
                            self,
                            Messaging.CARS)

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
                self.model.send_msg(Message(Message.INFORMATIF, "ok", self.discussion_nb),
                                    self,
                                    taxi)

            # Si ce n'est pas le meilleur taxi, envoie 'no'
            else:
                self.model.send_msg(Message(Message.INFORMATIF, "no", self.discussion_nb),
                                    self,
                                    taxi)
        self.taxis = []
        if self.best_taxi is not None:
            self.has_taxi = True
            self.send_time = 0
        self.best_taxi = None

    def disappear(self):
        self.model.send_msg(Message(Message.INFORMATIF, "disappear"), self)
        self.cell.remove_agent(self)
        self.model.agents.remove(self)
