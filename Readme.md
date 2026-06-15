# MesaGraphics: A Mesa Add-on for Pygame-Based Visualization

MesaGraphics is a visualization add-on for Mesa: https://Mesa.readthedocs.io/stable. It is inspired by Mesa's 
Solara-based visualization. The API closely mirrors Mesa's Solara-based visualization API, but runs entirely locally 
through Pygame.

**The project is a work in progress, so everything could change.**

## Using MesaGraphics

First, install Mesa. Installation instructions are available [here](https://Mesa.readthedocs.io/stable/). 
We use Mesa 3.5.1.

Then, install Pygame: 
```bash
pip install Pygame
```
Use Pygame 2.6.1 or later.


## How to use it

The visualization works very similarly to the Mesa's one. In fact, our main goal was to make simple switching from 
Solara to MesaGraphics. The differences are listed below.

### Imports

Import the MesaGraphics equivalents instead of the Solara functions. Replace the following Solara visualization 
imports with their MesaGraphics counterparts:
- `create_space_component`
- `make_space_component`
- `make_altair_space`
- `make_mpl_space_component`
- `make_plot_component`
- `make_mpl_plot_component`

Finally, in order to start the visualization, use `MesaGraphics` function instead of `SolaraViz`.

### Custom visualisation components

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
3. Import and use the MesaGraphics function `FigureMatplotlib` instead of the Solara's one:
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
    FigureMatplotlib(fig)
```

You can also create your own Pygame-based visualization functions. 
A custom visualization component is simply a function that takes a model as input and returns a `pg.Surface`.
