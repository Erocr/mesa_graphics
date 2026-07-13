import mesa
from Agent import Car, Obstacle


def average_turn_time(model):
    res = 0
    div = 0
    for agent in model.agents:
        if isinstance(agent, Car):
            div += 1
            if agent.last_turn_time == -1:
                res += agent.turn_time
            else:
                res += agent.last_turn_time
    return res / div


class Model(mesa.Model):
    def __init__(self, n=1, size=10, seed=None, configuration: int = 1):
        assert n <= size, "Trop de voitures dans un espace trop petit"
        super().__init__(seed=seed)
        self.num_agents = n
        self.datacollector = mesa.DataCollector(model_reporters={"turn time": average_turn_time})
        if configuration == 1:
            self.grid = mesa.discrete_space.OrthogonalVonNeumannGrid((size, 3), torus=True, random=self.random,
                                                                     capacity=1)
            car_possible_pos = self.grid.all_cells.select(lambda c: c.position[1] == 1).cells
            obstacles_pos = self.grid.all_cells.select(lambda c: c.position[1] == 2 or c.position[1] == 0).cells
        elif configuration == 2:
            self.grid = mesa.discrete_space.OrthogonalVonNeumannGrid((size, 4), torus=True, random=self.random,
                                                                     capacity=1)
            car_possible_pos = self.grid.all_cells.select(lambda c: c.position[1] == 1).cells
            obstacles_pos = self.grid.all_cells.select(lambda c: c.position[1] == 0 or c.position[1] == 3).cells
        else:
            raise NotImplementedError(f"configuration {configuration} not implemented")
        Obstacle.create_agents(self, len(obstacles_pos), obstacles_pos)
        Car.create_agents(self, n, [car_possible_pos[i] for i in range(n)])
        self.datacollector.collect(self)

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")

