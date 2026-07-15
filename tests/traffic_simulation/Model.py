import mesa
import numpy as np
from mesa.discrete_space import PropertyLayer

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


def average_speed(model):
    speeds = [agent.speed for agent in model.agents if isinstance(agent, Car)]
    return sum(speeds) / len(speeds)


class Model(mesa.Model):
    def __init__(self, n=1, size=10, max_speed=5, seed=None, configuration: int = 1):
        super().__init__(seed=seed)
        self.num_agents = n
        self.datacollector = mesa.DataCollector(model_reporters={"average turn time": average_turn_time,
                                                                 "average speed": average_speed})
        if configuration == 1:
            self.grid = mesa.discrete_space.OrthogonalVonNeumannGrid((size, 3), torus=True, random=self.random,
                                                                     capacity=1)
            self.car_possible_pos = self.grid.all_cells.select(lambda c: c.position[1] == 1).cells
            obstacles_pos = self.grid.all_cells.select(lambda c: c.position[1] == 2 or c.position[1] == 0).cells
        elif configuration == 2:
            self.grid = mesa.discrete_space.OrthogonalVonNeumannGrid((size, 4), torus=True, random=self.random,
                                                                     capacity=1)
            self.car_possible_pos = self.grid.all_cells.select(lambda c: c.position[1] == 1).cells
            obstacles_pos = self.grid.all_cells.select(lambda c: c.position[1] == 0 or c.position[1] == 3).cells
        elif configuration == 3:
            self.grid = mesa.discrete_space.OrthogonalVonNeumannGrid((size, 5), torus=True, random=self.random,
                                                                     capacity=1)

            def is_blocked(c):
                if c.position[1] == 0 or c.position[1] == 4: return True
                elif c.position[1] == 2: return c.position[0] != 2*size//3
                elif c.position[1] == 1: return False
                elif c.position[1] == 3: return c.position[0] > 2*size//3

            self.car_possible_pos = self.grid.all_cells.select(lambda c: c.position[1] == 3 or c.position[1] == 1).cells
            obstacles_pos = self.grid.all_cells.select(is_blocked).cells
        else:
            raise NotImplementedError(f"configuration {configuration} not implemented")
        assert n <= len(self.car_possible_pos), "Trop de voitures dans un espace trop petit"
        Obstacle.create_agents(self, len(obstacles_pos), obstacles_pos)
        Car.create_agents(self, n, [self.car_possible_pos[i] for i in range(n)], max_speed=max_speed)

        blocked_layer = PropertyLayer(
            "blocked", (self.grid.width, self.grid.height), default_value=0, dtype=int
        )
        blocked_layer.data = np.zeros((self.grid.width, self.grid.height))
        for c in obstacles_pos:
            blocked_layer.data[int(c.position[0])][int(c.position[1])] = 1
        self.grid.add_property_layer(blocked_layer)

        self.datacollector.collect(self)

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")

