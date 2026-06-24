from mesa_graphics.MesaGraphics import MesaGraphics

import mesa


class MoneyAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)

    def step(self):
        pass


class MoneyModel(mesa.Model):
    def __init__(self, seed=None):
        super().__init__(seed=seed)
        MoneyAgent.create_agents(model=self, n=5)

        self.datacollector = mesa.DataCollector(model_reporters={}, agent_reporters={})

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")


model = MoneyModel()

params = {
    "n": 0
}

MesaGraphics(model, model_params=params)
