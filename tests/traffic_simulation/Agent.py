import mesa


class Obstacle(mesa.discrete_space.CellAgent):
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass


class Car(mesa.discrete_space.CellAgent):
    """An agent with fixed initial wealth."""
    NUM_CAR = 0

    def __init__(self, model, cell, max_speed=5):
        super().__init__(model)
        self.last_turn_time = -1
        self.turn_time = 0
        self.max_speed = max_speed
        self.speed = 0
        self.cell = cell
        self.direction = (1, 0)
        self.num = Car.NUM_CAR
        Car.NUM_CAR += 1

    def step(self):
        for i in range(self.speed):
            if i >= self.speed: break

            def utility_func(c) -> int:
                """ 0 means impossible to go on, 1 means need to rotate to go on, and 2 is perfect (forward) """
                if not c.is_empty:
                    return 0
                pos = next_pos(self.model.grid, self.cell, self.direction)
                is_forward = c.position[0] == pos[0] and c.position[1] == pos[1]
                if is_forward:
                    return 2
                direction = get_direction(self.model.grid, self.cell.position, c.position)
                if direction[0] < 0:
                    return 0
                else:
                    # If the dot product of the directions is negative, it means that the position is behind
                    return (direction[0] * self.direction[0] + direction[1] * self.direction[1] >= 0) * 1

            best_cell = None
            best_utility = 0
            neighbors = self.cell.neighborhood.cells
            self.model.grid.random.shuffle(neighbors)
            for cell in neighbors:
                utility = utility_func(cell)
                if utility > best_utility:
                    best_cell = cell
                    best_utility = utility

            if best_utility == 0:
                self.speed = 0
                break

            if best_utility == 1:
                self.speed = max(self.speed, 2)
                self.direction = get_direction(self.model.grid, self.cell.position, best_cell.position)
                if i >= self.speed:
                    break
                self.move_to(best_cell)

            if best_utility == 2:
                self.move_to(best_cell)

            if self.cell.position[0] == 0 and self.direction[0] == 1:
                self.last_turn_time = self.turn_time
                self.turn_time = 0

        self.speed = min(self.speed+1, self.max_speed)
        self.turn_time += 1


def next_pos(grid, cell, direction):
    pos = [cell.position[0] + direction[0], cell.position[1] + direction[1]]
    if pos[0] >= grid.width: pos[0] = 0
    elif pos[0] < 0: pos[0] = grid.width - 1
    if pos[1] >= grid.height: pos[1] = 0
    elif pos[1] < 0: pos[1] = grid.height - 1
    return pos


def get_direction(grid, pos1, pos2):
    d = [pos2[0] - pos1[0], pos2[1] - pos1[1]]
    if d[0] < 0: d[0] += grid.width
    if d[0] > 1: d[0] -= grid.width
    if d[1] < 0: d[1] += grid.height
    if d[1] > 1: d[1] -= grid.height
    return d