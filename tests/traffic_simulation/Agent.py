import mesa


class CellInfo:
    def __init__(self, cell, is_free):
        self.cell = cell
        self.is_free = is_free

    def __str__(self):
        return str((self.cell, self.is_free))

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
        self.speed = 0
        self.cell = cell
        self.direction = (1, 0)
        self.num = Car.NUM_CAR
        Car.NUM_CAR += 1

    def step(self):
        perception = self.perceive()
        action = self.deliberate(perception)
        self.do(action)

    def perceive(self) -> list[list[CellInfo]]:
        """
        Perçois le monde.
        Renvoie les 3*max_speed cases qui sont devant la voiture en y associant les informations de la cellule
        Par exemple, avec un max_speed de 5, il peut renvoyer quelque chose qui ressemble schématiquement à ça :
        ...X..
        C....X
        XXXXXX

        Plus spécifiquement, il va renvoyer une grille de CellInfo, dont la définition est plus haut dans le fichier.
        Quelque chose comme :
        [[X, C, .], [X, ., .], [X, ., .], [X, ., X], [X, ., .], [X, X, .]]
        """
        res = []
        for i in range(Car.MAX_SPEED+1):
            res.append([None, None, None])
            for j in range(3):
                # La position dans la grille complète associée à la position (i, j) dans la grille partielle
                cell = self.partial_grid_to_cell(i, j)
                is_road = self.model.is_free(cell)
                res[i][j] = CellInfo(cell, is_road)

        return res

    def partial_grid_to_complete_grid(self, i, j):
        ortho_dir = (self.direction[1], -self.direction[0])
        p = [self.cell.position[0] + i * self.direction[0] + (j - 1) * ortho_dir[0],
             self.cell.position[1] + i * self.direction[1] + (j - 1) * ortho_dir[1]]

        # Applique le modulo du tore
        p[0] = p[0] % self.model.grid.width
        p[1] = p[1] % self.model.grid.height

        return p

    def partial_grid_to_cell(self, i, j):
        p = self.partial_grid_to_complete_grid(i, j)
        return self.model.grid.find_nearest_cell(p)

    def deliberate(self, perception: list[list[CellInfo]]) -> tuple[int, int]:
        """
        Choisis l'action à faire.
        Cette action est représentée comme un vecteur du mouvement qu'il aura.
        Pour ce faire, il va :
        - Créer un tableau de booléens avec la même dimension de la grille décrivant s'il peut aller sur la case ou pas.
        - Choisir la case la plus éloignée joignable (si plusieurs sont disponibles, en choisit un au hasard)
        :param perception: Grille des cases où il peut potentiellement aller
        :return: tuple[int, int]
        """

        # Crée la grille des mouvements possibles
        grid = [[False, False, False] for _ in range(self.MAX_SPEED + 1)]
        for i in range(self.MAX_SPEED+1):
            for j in range(1, 4):  # On veut commencer la boucle avec la case du milieu
                j = j % 3
                if j == 1:  # Si la case est devant la voiture
                    # Regarde si c'est la tuile où est déjà la voiture (i == 0) ou si la tuile d'avant est accessible,
                    # et la tuile est libre.
                    # Enfin, elle ne doit pas être trop éloignée.
                    grid[i][j] = i == 0 or (grid[i-1][j] and perception[i][j].is_free and i <= self.speed)
                else:
                    # La case est accessible si la case du milieu est accessible, et que la case est libre
                    grid[i][j] = grid[i][1] and perception[i][j].is_free and i + abs(j-1) <= self.speed

        # Cherche les positions les plus éloignées
        max_dist = 0
        best_choices = []
        for i in range(self.MAX_SPEED+1):
            for j in range(3):
                if not grid[i][j]:
                    continue

                d = i * 2 + abs(j - 1)  # On veut qu'un chemin tout droit soit préféré par rapport à un chemin sur le
                                        # côté
                if d == max_dist:
                    best_choices.append((i, j))
                if d > max_dist:
                    best_choices = [(i, j)]
                    max_dist = d

        return self.random.choice(best_choices)

    def do(self, action: tuple[int, int]) -> None:
        cell = self.partial_grid_to_cell(*action)
        self.move_to(cell)

        # Diminue ou augmente la vitesse en fonction des cas
        if action[0] + abs(action[1] - 1) < self.speed:
            self.speed = 0
        elif action[1] == 1:
            self.speed = min(self.MAX_SPEED, self.speed + 1)
        else:
            self.speed = min(self.MAX_SPEED_TURINING, self.speed)

        # Change la direction
        if action[1] == 0:
            self.direction = (-self.direction[1], self.direction[0])  # Tourne vers la gauche
        elif action[1] == 2:
            self.direction = (self.direction[1], -self.direction[0])  # Tourne vers la droite


def get_direction(grid, pos1, pos2):
    d = [pos2[0] - pos1[0], pos2[1] - pos1[1]]
    if d[0] < 0: d[0] += grid.width
    if d[0] > 1: d[0] -= grid.width
    if d[1] < 0: d[1] += grid.height
    if d[1] > 1: d[1] -= grid.height
    return d
