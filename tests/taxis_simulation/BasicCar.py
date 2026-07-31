from Agent import MessageReceiver, Passenger, CellInfo
from Messaging import Message
from a_star_algorithm import a_star


class BasicCar(MessageReceiver):
    """An agent with fixed initial wealth."""
    TIME_BEFORE_RECOMPUTING_PATH = 2

    NUM_CAR = 0
    MAX_SPEED = 5
    MAX_SPEED_TURNING = 2

    # Les différents états de l'agent
    IDLE = 0
    SENT_PROPOSITION = 1
    PROPOSITION_ACCEPTED = 2
    TRANSPORTING = 3

    def __init__(self, model, cell, max_speed=5):
        BasicCar.MAX_SPEED = max_speed
        super().__init__(model)
        self.pos_counter = 0
        self.speed = 0
        self.cell = cell
        self.direction = self.starting_direction()
        self.num = BasicCar.NUM_CAR
        BasicCar.NUM_CAR += 1

        self.state = BasicCar.IDLE  # Son état

        self.sent_proposition = None  # Le passager à qui il a proposé de le transporter
        self.discussion_nb = 0  # Le numéro de discussion avec le passager
        self.route_computed = ""  # La route pour aller jusqu'au passager à qui il a proposé

        self.transport = None  # The passenger he transports

        # Le chemin est sous la forme d'une chaîne de caractères où chaque caractère indique une direction
        # f pour forward, r pour right et l pour left
        self.path = ""
        self.goal = None  # Là vers où il va
        self.follow_path = False

        self.sent_proposition_timer = 0
        self.blocked_timer = 0  # Depuis quand est-ce qu'il est bloqué et qu'il ne peut pas avancer

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

    def perceive(self):
        """
        Perçois le monde.

        Renvoie la case de devant et les cases sur le côté dans l'ordre : [gauche, devant, droite].
        Renvoie des CellInfo correspondant aux cases.

        Enfin, il renvoie un descriptif de ce qu'il a trouvé dans la boîte aux lettres.
        S'il est en IDLE : il renvoie le passager le plus proche s'il y a au moins un passager, et None sinon.
        S'il est en SENT_PROPOSITION : il renvoie True si la personne a accepté sa proposition, False s'il l'a refusé,
        et None s'il n'a pas répondu.
        S'il est en PROPOSITION_ACCEPTED : il renvoie "disappear" si la personne disparaît, et None sinon
        S'il est en TRANSPORTING : il renvoie "disappear" si la personne disparaît, la direction vers laquelle la
        personne veut aller si elle l'annonce, et None s'il n'a rien reçu de spécial.
        """
        directions = [self.left_dir(), self.direction, self.right_dir()]
        positions = [(self.cell.position[0] + d[0], self.cell.position[1] + d[1]) for d in directions]
        res = []

        for j in range(3):
            # La position dans la grille complète associée à la position (i, j) de la grille partielle
            cell = self.model.grid.find_nearest_cell(positions[j])
            is_road = self.model.is_road(cell)
            blocking = self.model.blocking(cell)
            accepted_dirs = self.model.accepted_directions(cell)
            res.append(CellInfo(cell, is_road, accepted_dirs, blocking))

        res += [self.read_messages()]

        return res

    def read_messages(self):
        """
        Lit les messages.
        Cette fonction peut aussi supprimer les messages.
        Enfin, elle renvoie un descriptif de ce qu'il a trouvé dans la boîte aux lettres.

        S'il est en IDLE : il renvoie le passager le plus proche s'il y a au moins un passager, et None sinon.
        S'il est en SENT_PROPOSITION : il renvoie True si la personne a accepté sa proposition, False s'il l'a refusé,
        et None s'il n'a pas répondu.
        S'il est en PROPOSITION_ACCEPTED : il renvoie "disappear" si la personne disparaît, et None sinon
        S'il est en TRANSPORTING : il renvoie "disappear" si la personne disparaît, la direction vers laquelle la
        personne veut aller si elle l'annonce, et None s'il n'a rien reçu de spécial.
        """
        # Si la voiture n'a pas de passagers, et n'est pas en train d'aller vers un passager
        if self.state == BasicCar.IDLE:
            # Parmi toutes les propositions des passagers, calcule le passager le plus proche
            best_passenger = None
            min_distance = 100000
            discussion_nb = 0
            for i in reversed(range(len(self.messages))):
                message, sender = self.messages.pop(i)

                # Si le message est une proposition d'un passager
                # Le protocole pour les passagers est d'envoyer 'passenger posX posY' aux taxis qui pourraient le
                # transporter
                if message.performatif == Message.REQUEST and message.content[:9] == "passenger":
                    # Extrait la position du passager
                    splitted = message.content.split(" ")
                    pos = int(splitted[1]), int(splitted[2])

                    # Calcule la route la plus rapide jusqu'au passager
                    goal = self.model.grid.find_nearest_cell(pos)
                    route_computed = a_star(self.cell, goal, self.direction, self.model)

                    # Si jamais la route est plus courte que celle vers le passager le plus proche jusque-là
                    if len(route_computed) < min_distance:
                        min_distance = len(route_computed)
                        best_passenger = sender
                        self.route_computed = route_computed  # Mémorise la route calculée
                        self.goal = goal
                        discussion_nb = message.discussion_nb

            return best_passenger, discussion_nb

        # Si jamais il a envoyé une proposition à quelqu'un, mais que personne n'a répondu encore
        elif self.state == BasicCar.SENT_PROPOSITION:
            for i in reversed(range(len(self.messages))):
                message, sender = self.messages.pop(i)

                # Si jamais le message est
                # - est une acceptation
                # - est envoyée par le passager à qui il a envoyé la proposition
                # - est dans la même discussion que celle de la proposition
                if message.performatif == Message.INFORMATIF and message.content == "ok" and \
                        message.discussion_nb == self.discussion_nb and sender == self.sent_proposition:

                    return True

                # Si jamais le message
                # - est une réfutation
                # - est envoyée par le passager à qui il a envoyé la proposition
                # - est dans la même discussion que celle de la proposition
                elif message.performatif == Message.INFORMATIF and message.content == "no" and \
                        sender == self.sent_proposition and message.discussion_nb == self.discussion_nb:

                    return False

        # Si le passager a accepté sa proposition
        elif self.state == BasicCar.PROPOSITION_ACCEPTED:
            for i in reversed(range(len(self.messages))):
                message, sender = self.messages.pop(i)

                # Si jamais la personne vers qui il va disparaît
                if message.performatif == Message.INFORMATIF and message.content == "disappear" and \
                        self.sent_proposition == sender:

                    return "disappear"

        elif self.state == BasicCar.TRANSPORTING:
            for i in reversed(range(len(self.messages))):
                message, sender = self.messages.pop(i)

                # Si le passager envoie là où il veut aller
                if message.performatif == Message.INFORMATIF and message.content[:9] == "direction" and \
                        message.discussion_nb == self.discussion_nb and sender == self.transport:

                    return message.content

                # Si jamais la personne qu'il transporte disparait
                if message.performatif == Message.INFORMATIF and message.content == "disappear" and \
                        self.transport == sender:

                    return "disappear"

    def left_dir(self):
        """ La direction tournée de 90° vers la gauche """
        return -self.direction[1], self.direction[0]

    def right_dir(self):
        """ La direction tournée de 90° vers la droite """
        return self.direction[1], -self.direction[0]

    def deliberate(self, perception: list) -> list:
        """
        Renvoie une liste d'actions.
        Le premier élément est la meilleure direction vers laquelle il peut aller.
        Ensuite, les actions peuvent être :
        - des tuples (Message, à qui l'envoyer)

        :param perception: Les cases où il pourra potentiellement aller, avec plusieurs attributs associés à la case
        :return: le vecteur de mouvement sur la grille
        """
        actions = []

        # S'il n'a rien à faire
        if self.state == BasicCar.IDLE:

            # S'il a reçu au moins une proposition d'un passager, lui envoie un message, et change d'état
            if perception[3] is not None and perception[3][0] is not None:
                best_passenger, discussion_nb = perception[3]

                # Demande à self.do d'envoyer un message
                actions.append((Message(Message.INFORMATIF,
                                        f"distance {len(self.route_computed)}",
                                        discussion_nb),
                                best_passenger))
                self.sent_proposition = best_passenger
                self.discussion_nb = discussion_nb

                # S'arrête, le chemin qu'il a calculé serait obsolète sinon
                self.follow_path = True
                self.path = ""

                # Change son état
                self.state = BasicCar.SENT_PROPOSITION
                self.sent_proposition_timer = 0

        elif self.state == BasicCar.SENT_PROPOSITION:

            self.sent_proposition_timer += 1

            # Si la personne a accepté la proposition de la voiture
            if perception[3] is not None and perception[3]:
                # Va vers ce passager
                self.path = self.route_computed
                self.follow_path = True

                # Change son état
                self.state = BasicCar.PROPOSITION_ACCEPTED

            # Si la personne a refusé la proposition ou si la personne prend trop de temps pour répondre
            elif (perception[3] is not None and not perception[3]) or \
                    self.sent_proposition_timer > Passenger.TIME_WAIT_BEFORE_ACCEPT:

                #  Oublie d'avoir envoyé cette proposition
                self.sent_proposition = None
                self.route_computed = ""
                self.follow_path = False

                # Passe en état IDLE
                self.state = BasicCar.IDLE

        elif self.state == BasicCar.PROPOSITION_ACCEPTED:

            if self.sent_proposition.cell == self.cell:
                self.transport = self.sent_proposition
                self.sent_proposition = None
                self.transport.transported_by(self)
                self.state = BasicCar.TRANSPORTING

            # Si la personne disparaît
            elif perception[3] is not None and perception[3] == "disappear":
                # Oublie la personne
                self.sent_proposition = None
                self.follow_path = False
                # Rentre en état IDLE
                self.state = BasicCar.IDLE

        elif self.state == BasicCar.TRANSPORTING:

            # Si la personne disparaît (par exemple si elle arrive à destination)
            if perception[3] is not None and perception[3] == "disappear":
                # Oublie la personne
                self.transport = None
                self.follow_path = False
                # Rentre en état IDLE
                self.state = BasicCar.IDLE

            # S'il reçoit là où le passager veut aller, il y va
            elif perception[3] is not None and perception[3][:9] == "direction":
                # Les coordonnées de là où il veut aller
                splitted = perception[3].split(" ")
                pos = int(splitted[1]), int(splitted[2])

                # Calcule le chemin
                goal = self.model.grid.find_nearest_cell(pos)
                self.path = a_star(self.cell, goal, self.direction, self.model)
                self.goal = goal
                self.follow_path = True

        if not self.state == BasicCar.IDLE:
            return self.deliberation_with_path(perception) + actions
        else:
            return self.deliberation_without_path(perception) + actions

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

        return [direction]

    def deliberation_with_path(self, perception):
        """ Donne la direction de son chemin s'il peut y aller, sinon il renvoie (0, 0) """
        # Si son chemin est vide, n'avance pas
        if len(self.path) == 0:
            return [(0, 0)]

        # S'il doit aller à gauche, et qu'il peut aller à gauche
        if self.path[0] == "l" and self.can_go(self.left_dir(), perception[0]):
            return [self.left_dir()]

        # S'il doit aller tout droit, et qu'il peut aller tout droit
        elif self.path[0] == "f" and self.can_go(self.direction, perception[1]):
            return [self.direction]

        # S'il doit aller à droite, et qu'il peut aller à droite
        elif self.path[0] == "r" and self.can_go(self.right_dir(), perception[2]):
            return [self.right_dir()]

        # S'il ne peut pas aller là où il doit aller
        else:
            self.blocked_timer += 1

            # Si ça fait plusieurs tours qu'il ne peut pas avancer
            if self.blocked_timer > self.TIME_BEFORE_RECOMPUTING_PATH:
                self.blocked_timer = 0

                # Trouve la cellule où il veut aller, mais n'arrive pas à aller
                direction = {"f": self.direction, "l": self.left_dir(), "r": self.right_dir()}[self.path[0]]
                blocking_pos = self.cell.position[0] + direction[0], self.cell.position[1] + direction[1]
                blocking_cell = self.model.grid.find_nearest_cell(blocking_pos)

                # Recalcule le chemin sans passer par blocking_cell
                path = a_star(self.cell, self.goal, self.direction, self.model, [blocking_cell])

                # Remplace seulement s'il a trouvé un chemin
                if path is not None:
                    self.path = path

                    # Recalcule là où il va en fonction du nouveau chemin
                    return self.deliberation_with_path(perception)

            return [(0, 0)]

    def increment_speed(self):
        self.speed = min(self.speed + 1, BasicCar.MAX_SPEED)

    def can_go(self, direction: tuple[int, int], cellInfo: CellInfo):
        return cellInfo.is_road and cellInfo.blocking is None and direction in cellInfo.directions

    def do(self, deliberation: list) -> None:
        """
        """
        direction = deliberation[0]
        if direction == (0, 0):  # S'il n'avance pas
            self.speed = 0  # Pile
        elif direction == self.direction:  # S'il va tout droit
            self.increment_speed()  # Accélère
        else:  # S'il tourne
            self.speed = min(self.speed + 1, BasicCar.MAX_SPEED_TURNING)

        # Incrémente le compteur
        self.pos_counter += self.speed
        if self.pos_counter >= BasicCar.MAX_SPEED:
            self.pos_counter -= BasicCar.MAX_SPEED
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

        # Gère les actions supplémentaires (ici l'envoi de messages)
        for action in deliberation[1:]:
            if isinstance(action, tuple) and isinstance(action[0], Message):
                self.model.send_msg(action[0], self, action[1])