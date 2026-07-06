import mesa
from mesa.discrete_space import CellAgent
from mesa.visualization.components import AgentPortrayalStyle
from mesa.visualization.space_renderer import SpaceRenderer
import mesa.visualization.user_param as mesa_user_param

from mesa_graphics import make_mpl_plot_component, MesaGraphics


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


def sum_money(model):
    return sum([agent.wealth for agent in model.agents])


class MoneyModel(mesa.Model):
    def __init__(self, n=10, capacity=50, boolean=True, selection="none", text="none", seed=None):
        print(f"arguments are:\n n={n}\n capacity={capacity}\n boolean={boolean}\n seed={seed}\n selection={selection}\n text={text}")
        super().__init__(seed=seed)
        self.num_agents = n
        self.datacollector = mesa.DataCollector(model_reporters={"Gini": compute_gini,
                                                                 "SumMoney": sum_money},
                                                agent_reporters={"Wealth": "wealth"})
        self.grid = mesa.discrete_space.OrthogonalVonNeumannGrid((6, 6), torus=True, random=self.random, capacity=capacity)
        choices = self.random.choices(self.grid.all_cells.cells, k=self.num_agents)
        MoneyAgent.create_agents(self, n, choices)
        self.datacollector.collect(self)

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")

    def tax(self, amount=1):
        for agent in self.agents:
            agent.wealth = max(0, agent.wealth - amount)


money_model = MoneyModel()


def agent_portrayal(agent):
    return AgentPortrayalStyle(color="tab:orange", size=50)


renderer = SpaceRenderer(model=money_model, backend="matplotlib")
renderer.setup_agents(agent_portrayal)
renderer.render()

GiniPlot = make_mpl_plot_component("Gini", page=1)
SumMoneyPlot = make_mpl_plot_component("SumMoney", page=0)


model_params = {
    "selection": {
        "type": "Select",
        "value": "selection1",
        "values": ["selection1", "selection2", "selection3", "selection4"]
    },
    "n": {
        "type": "SliderInt",
        "value": 5,
        "label": "number of agents",
        "min": 1,
        "max": 40,
        "step": 1,
    },
    "text": {
        "type": "InputText",
        "value": "hello"
    },
    "capacity": 50,
}

custom_buttons = {
    "tax": {
        "amount": {
            "type": "SliderInt",
            "value": 1,
            "min": 1,
            "max": 5,
            "step": 1
        }
    }
}

page = MesaGraphics(
    money_model,
    renderer,
    model_params=model_params,
    components=[SumMoneyPlot, GiniPlot],
    custom_method_call=custom_buttons
)

