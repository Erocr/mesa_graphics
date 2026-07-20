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


class Car(mesa.discrete_space.CellAgent):
    """An agent with fixed initial wealth."""
    NUM_CAR = 0
    MAX_SPEED = 5
    MAX_SPEED_TURINING = 2

    def __init__(self, model, cell, max_speed=5):
        Car.MAX_SPEED = max_speed
        super().__init__(model)
        self.pos_counter = 0
        self.speed = 0
        self.cell = cell
        self.direction = (1, 0)
        self.num = Car.NUM_CAR
        Car.NUM_CAR += 1

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

    def increment_speed(self):
        self.speed = min(self.speed + 1, Car.MAX_SPEED)

    def can_go(self, direction: tuple[int, int], cellInfo: CellInfo):
        return cellInfo.is_free and direction in cellInfo.directions

    def do(self, direction: tuple[int, int]) -> None:
        """
        """
        if direction == (0, 0):  # S'il ne peut aller nul part
            self.speed = 0  # Pile
        elif direction == self.direction:  # S'il peut aller tout droit
            self.increment_speed()  # Accélère
        else:  # S'il peut tourner
            self.speed = min(self.speed + 1, Car.MAX_SPEED_TURINING)

        # Incrémente le compteur
        self.pos_counter += self.speed
        if self.pos_counter >= Car.MAX_SPEED:
            self.pos_counter -= Car.MAX_SPEED
            if direction != (0, 0):
                self.direction = direction  # Tourne la voiture

            # Avance la voiture
            position = self.cell.position[0] + direction[0], self.cell.position[1] + direction[1]
            self.move_to(self.model.grid.find_nearest_cell(position))


class TrafficLight(mesa.discrete_space.CellAgent):
    def __init__(self, model, cell, time=5, states=None):
        assert states is not None and len(states) > 0, \
            "Les feu de signalisation (traffic light) doivent avoir un paramètre states non vide"
        super().__init__(model)
        self.cell = cell
        self.state_duration = time
        self.counter_time = 0
        self.states = states
        self.state_index = 0

    def step(self):
        self.counter_time += 1
        if self.counter_time >= self.state_duration:
            self.counter_time -= self.state_duration

            self.state_index = (self.state_index + 1) % len(self.states)
            self.model.modify_directions(self.cell, self.states[self.state_index])

