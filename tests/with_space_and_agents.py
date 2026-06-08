import mesa
from mesa.discrete_space import CellAgent
from mesa.visualization.components import AgentPortrayalStyle
from mesa.visualization.space_renderer import SpaceRenderer

from mesa_graphics.MesaGraphics import MesaGraphics
from mesa_graphics.matplotlib_components import make_mpl_plot_component


class MoneyAgent(CellAgent):
    """An agent with fixed initial wealth."""

    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        self.wealth = 10

    def step(self):
        cell = self.random.choice(self.cell.neighborhood.cells)
        self.move_to(cell)
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
        self.datacollector = mesa.DataCollector(model_reporters={"Gini": compute_gini},
                                                agent_reporters={"Wealth": "wealth"})
        self.grid = mesa.discrete_space.HexGrid((6, 6), torus=True, random=self.random)
        choices = self.random.choices(self.grid.all_cells.cells, k=self.num_agents)
        MoneyAgent.create_agents(self, n, choices)
        self.datacollector.collect(self)

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")


money_model = MoneyModel()


def agent_portrayal(agent):
    return AgentPortrayalStyle(color="tab:orange", size=50)


renderer = SpaceRenderer(model=money_model, backend="matplotlib")
renderer.setup_agents(agent_portrayal)
renderer.render()

GiniPlot = make_mpl_plot_component("Gini", page=0)

page = MesaGraphics(
    money_model,
    renderer,
    components=[GiniPlot],
)
