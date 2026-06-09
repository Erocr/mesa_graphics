from mesa_graphics.MesaGraphics import MesaGraphics

import mesa


class MoneyAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)

    def step(self):
        pass


class MoneyModel(mesa.Model):
    def __init__(self, n=5, seed=None):
        super().__init__(seed=seed)
        MoneyAgent.create_agents(model=self, n=n)

        self.datacollector = mesa.DataCollector(model_reporters={}, agent_reporters={})

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")


model = MoneyModel()

model_params = {
    "n": {
        "type": "SliderInt",
        "value": 5,
        "label": "Number of agents:",
        "min": 0,
        "max": 10,
        "step": 1,
    },
    "seed": {
        "type": "SliderInt",
        "value": 1,
        "min": 0,
        "max": 100,
        "step": 1,
    }
}

MesaGraphics(model, model_params=model_params)
