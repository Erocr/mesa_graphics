# MesaGraphics: A Mesa Add-on for Pygame-Based Visualization

MesaGraphics is a visualization add-on for Mesa: https://Mesa.readthedocs.io/stable. It is inspired by Mesa's 
Solara-based visualization. The API closely mirrors Mesa's Solara-based visualization API, but runs entirely locally 
through Pygame.

![screenshot](doc/screenshot.png)

**The project is a work in progress, so everything could change.**

## Why MesaGraphics?

MesaGraphics provides a local visualization backend for Mesa models.

Compared to Solara-based visualization:

- No web browser required
- Runs entirely locally through Pygame
- Simple migration path from existing Solara visualizations
- Suitable for desktop applications and teaching environments

## Installation

### Requirements

- Mesa 3.5.1
- Pygame 2.6.1+

### Install Mesa 3.5.1

Detailed installation instructions are available [here](https://Mesa.readthedocs.io/stable/). 
Use Mesa 3.5.1.

To install the latest stable Mesa release, run:

```bash
pip install mesa
```

You need also networkx, altair, matplolib and solara:

```bash
pip install networkx altair matplotlib solara
```

### Install pygame 2.6.1 or later
 
```bash
pip install pygame
```
Use Pygame 2.6.1 or later.

### Install MesaGraphics

Start by cloning the repository in your project folder 
```bash
cd projectFolder
git clone --filter=blob:none --sparse https://github.com/Erocr/mesa_graphics.git
cd mesa_graphics
git sparse-checkout set mesa_graphics
```
This command clone only the part of the repository with the source code.  
If git is not installed on your computer, or you have problems, you can go directly on 
[the github page](https://github.com/Erocr/mesa_graphics), then click on the green Code button, download ZIP, and 
extract the ZIP file in your project folder.

## How to use it

The visualization works very similarly to the Mesa's one. In fact, MesaGraphics was designed to make migration from 
Solara visualizations as straightforward as possible. In most cases, migrating an existing visualization only requires 
updating imports and removing Solara-specific decorators.

You can find tutorials for the Solara visualization [here](https://mesa.readthedocs.io/stable/getting_started.html).



### Imports

This module use many functions from the mesa.visualization package. Only a few functions are changed in MesaGraphics. 
Though, we kept the same name for a majority of these functions. So, in order to make the migration, just change some 
imports.

Replace the following Solara visualization imports with their MesaGraphics counterparts:
- `create_space_component`
- `make_space_component`
- `make_altair_space`
- `make_mpl_space_component`
- `make_plot_component`
- `make_mpl_plot_component`

Finally, in order to start the visualization, use `MesaGraphics` function instead of `SolaraViz`.

For example, the following imports:
```python
from mesa.visualization import (
    make_plot_component,
    make_space_component,
    SolaraViz
)
from mesa.visualization.user_param import Slider
```
become:
```python
from mesa_graphics import (
    make_plot_component,
    make_space_component,
    MesaGraphics
)
from mesa.visualization.user_param import Slider
```

### Custom visualization components

Custom visualization components are user-defined functions that generate graphical elements.
With Solara, the syntax looks like:
```python
@solara.component
def Histogram(model):
    update_counter.get()  # This is required to update the counter
    # Note: you must initialize a figure using this method instead of
    # plt.figure(), for thread safety purpose
    fig = Figure()
    ax = fig.subplots()
    wealth_vals = [agent.wealth for agent in model.agents]
    # Note: you have to use Matplotlib's OOP API instead of plt.hist
    # because plt.hist is not thread-safe.
    ax.hist(wealth_vals, bins=10)
    solara.FigureMatplotlib(fig)
```


With MesaGraphics, you must not use Solara's functions. You must:
1. remove `@solara.component`, it is no more necessary.
2. remove `update_counter.get()`. It is not mandatory to remove it, but it is not needed in the MesaGraphics 
architecture.
3. Import and use the MesaGraphics function `FigureMatplotlib` instead of the Solara's one. Moreover, you shall return 
the result of the function:
`from mesa_graphics.backend_integration import FigureMatplotlib`

So the function above becomes:
```python
from mesa_graphics.backend_integration import FigureMatplotlib

def Histogram(model):
    # Note: you must initialize a figure using this method instead of
    # plt.figure(), for thread safety purpose
    fig = Figure()
    ax = fig.subplots()
    wealth_vals = [agent.wealth for agent in model.agents]
    # Note: you have to use Matplotlib's OOP API instead of plt.hist
    # because plt.hist is not thread-safe.
    ax.hist(wealth_vals, bins=10)
    return FigureMatplotlib(fig)
```

You can also create your own Pygame-based visualization functions. 
A custom visualization component is simply a function that takes a model as input and returns a `pg.Surface`.

For example:
```python
import pygame as pg

def WhiteComponent(model):
    res = pg.Surface((100, 100))
    res.fill((255, 0, 0))
    return res
``` 
This function is a valid component that draws a red rectangle.

### Summarize

To make the migration from Solara's view to MesaGraphics, follow these steps:
1. Import MesaGraphics functions instead of their mesa.visualization counterparts.
2. Replace SolaraViz with MesaGraphics
3. Change the custom visualization components

### A full example


The following code use Solara to visualize the Boltzmann wealth Model (found in the getting started tutorial of mesa).
This example has a space renderer, a normal plot component, and a custom component.
We added comments to describe what change.
```python
import solara
import mesa
from matplotlib.figure import Figure
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid
from mesa.visualization.utils import update_counter
from mesa.visualization import SolaraViz, SpaceRenderer, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle

""" We change this imports:
import solara                                                                 # to remove
import mesa                                                                   # same
from matplotlib.figure import Figure                                          # same                                         
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid                # same
from mesa.visualization.utils import update_counter                           # can be removed
from mesa_graphics import MesaGraphics, make_plot_component                   # changed
from mesa_graphics import FigureMatplotlib                                    # added (for the custom component)
from mesa.visualization import SpaceRenderer                                  # same
from mesa.visualization.components import AgentPortrayalStyle                 # same
"""

def compute_gini(model):
    agent_wealths = [agent.wealth for agent in model.agents]
    x = sorted(agent_wealths)
    N = model.num_agents
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return 1 + (1 / N) - 2 * B


class MoneyAgent(CellAgent):
    """An agent with fixed initial wealth."""

    def __init__(self, model, cell):
        """initialize a MoneyAgent instance.

        Args:
            model: A model instance
        """
        super().__init__(model)
        self.cell = cell
        self.wealth = 1

    def move(self):
        """Move the agent to a random neighboring cell."""
        self.cell = self.cell.neighborhood.select_random_cell()

    def give_money(self):
        """Give 1 unit of wealth to a random agent in the same cell."""
        cellmates = [a for a in self.cell.agents if a is not self]

        if cellmates:  # Only give money if there are other agents present
            other = self.random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1

    def step(self):
        """do one step of the agent."""
        self.move()
        if self.wealth > 0:
            self.give_money()


class MoneyModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, n=10, width=10, height=10, seed=None):
        """Initialize a MoneyModel instance.

        Args:
            N: The number of agents.
            width: width of the grid.
            height: Height of the grid.
        """
        super().__init__(seed=seed)
        self.num_agents = n
        self.grid = OrthogonalMooreGrid((width, height), random=self.random)

        # Create agents
        MoneyAgent.create_agents(
            self,
            self.num_agents,
            self.random.choices(self.grid.all_cells.cells, k=self.num_agents),
        )

        self.datacollector = mesa.DataCollector(
            model_reporters={"Gini": compute_gini}, agent_reporters={"Wealth": "wealth"}
        )
        self.datacollector.collect(self)

    def step(self):
        """do one step of the model"""
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)


def agent_portrayal(agent):
    return AgentPortrayalStyle(color="tab:orange", size=50)


model_params = {
    "n": {
        "type": "SliderInt",
        "value": 50,
        "label": "Number of agents:",
        "min": 10,
        "max": 100,
        "step": 1,
    },
    "width": 10,
    "height": 10,
}

plot_comp = make_plot_component("encoding", page=1)


# Create initial model instance
money_model = MoneyModel(n=50, width=10, height=10)  # keyword arguments

renderer = (
    SpaceRenderer(model=money_model, backend="matplotlib")
    .setup_agents(agent_portrayal)
    .render()
)

GiniPlot = make_plot_component("Gini", page=1)


@solara.component
def Histogram(model):
    update_counter.get()
    fig = Figure()
    ax = fig.subplots()
    wealth_vals = [agent.wealth for agent in model.agents]
    ax.hist(wealth_vals, bins=10)
    solara.FigureMatplotlib(fig)
    
""" We modify the function
# solara.component removed
def Histogram(model):
    update_counter.get()  # Not necessary, can be removed
    fig = Figure()
    ax = fig.subplots()
    wealth_vals = [agent.wealth for agent in model.agents]
    ax.hist(wealth_vals, bins=10)
    return FigureMatplotlib(fig)  # returns the FigureMatplotlib from MesaGraphics
"""


page = SolaraViz(
    money_model,
    renderer,
    components=[GiniPlot, (Histogram, 2)],
    model_params=model_params,
    name="Boltzmann Wealth Model",
)

""" Use MesaGraphics instead of SolaraViz
page = MesaGraphics(
    money_model,
    renderer,
    components=[GiniPlot, (Histogram, 2)],
    model_params=model_params,
    name="Boltzmann Wealth Model",
)
"""
```

