# MesaGraphics: A Mesa Add-on for Pygame-Based Visualization

MesaGraphics is an add-on for the Mesa library: https://Mesa.readthedocs.io/stable. It is inspired by Mesa's 
Solara-based visualization. The API is almost the same as the Solara-based one, but this time, it runs locally. 
Moreover, it also introduces several additional features and improvements.

**The project is a work in progress, so everything could change.**

## Using MesaGraphics

First, install Mesa. Installation instructions are available [here](https://Mesa.readthedocs.io/stable/). 
We use mesa 3.5.1.

Then, install pygame : 
```bash
pip install pygame
```
Use pygame 2.6.1 or later.


## How to use it

The visualization works very similarly to the Mesa's one. In fact, our main goal was to make simple switching from 
Solara to MesaGraphics. Here the changes.

### Imports

You have to import our functions instead of solara's functions. The list of functions you have to import instead of 
Mesa's one:
- `create_space_component`
- `make_space_component`
- `make_altair_space`
- `make_mpl_space_component`
- `make_plot_component`
- `make_mpl_plot_component`

Finally, in order to start the visualization, use `MesaGraphics` function instead of `SolaraViz`.

### Custom visualisation components

The custom visualization components are user's created functions that create solara's components. Here they will be 
changed. **This part is a work in progress**

