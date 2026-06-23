import mesa

from mesa_graphics.MesaGraphics import MesaGraphics
from mesa_graphics.components import make_mpl_plot_component


class MoneyAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, model):
        super().__init__(model)
        self.wealth = 10

    def step(self):
        agent = self.random.choice(self.model.agents)
        exchange = self.wealth // 2
        agent.wealth += exchange
        self.wealth -= exchange


def compute_gini(model):
    agent_wealths = [agent.wealth for agent in model.agents]
    x = sorted(agent_wealths)
    n = model.num_agents
    B = sum(xi * (n - i) for i, xi in enumerate(x)) / (n * sum(x))
    return 1 + (1 / n) - 2 * B


class MoneyModel(mesa.Model):
    def __init__(self, n=10, seed=None):
        super().__init__(seed=seed)
        self.num_agents = n
        MoneyAgent.create_agents(model=self, n=n)
        self.datacollector = mesa.DataCollector(model_reporters={"Gini": compute_gini},
                                                agent_reporters={"Wealth": "wealth"})

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")


money_model = MoneyModel()

GiniPlot = make_mpl_plot_component("Gini", page=0)

page = MesaGraphics(
    money_model,
    components=[GiniPlot]*15,
)
