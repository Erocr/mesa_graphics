# Developer documentation

This documentation is intended for developers who want to contribute to the project.
It explains what this project does and how it does it.

## Features

MesaGraphics is a visualization add-on for Mesa: https://Mesa.readthedocs.io/stable. 

The user defines a Mesa Model, then, the MesaGraphics library displays the Model, and the user-defined plots. It 
allows the user to interact with the Model, and re-instantiate it through buttons, checkboxes, and sliders.

![screenshot](screenshot.png)

It is inspired by Mesa's Solara-based visualizations. The API closely mirrors Mesa's Solara-based visualization API, but runs 
entirely locally through Pygame.

### Components

Components are dynamic plots that track Model attributes, and being refreshed every time the user's Model is 
modified.
There are multiple ways to create components:
- Though Mesa's Renderer (the class name is SpaceRenderer) create the space plots. It shows a grid with the agents 
in it.
- Though make_plot_component function. The function creates a plot that track the value of an attribute
(or the result of a function).
- Custom components, for more complex plots.

These functions are implemented in the components.py file.

Each component is associated with a page. This page is the one in which it will be drawn (0 by default). The 
components are drawn in the order chosen by the user when their page is the currently selected page.

The user can change the page with buttons.

### Model Parameters

The user can define model parameters dynamically (the elements in the left column in the image). 

When the user clicks on "RESET", the Model is re-instantiated. 
The parameters chosen to re-instantiate the Model are the one selected using sliders, or checkboxes.


## Dev environment setup

First, make sure that you are allowed to contribute. 
If you are unable to contribute to this repository for any reason, you are free to copy the code into a new repository 
and build upon it.

### Installation

In the user's documentation, there is a command line that clone only the folder with the source code, but here you need
all the folders.

```bash
git clone "https://github.com/Erocr/mesa_graphics.git"
```


Install the following requirements: numpy, matplotlib, mesa, networkx, altair, solara, pygame
We tested it with the following versions:
- Pygame 2.6.1+
- Mesa 3.5.1

```bash
pip install networkx altair matplotlib solara pygame mesa
```
altair and matplotlib are facultatif, it depends on the backend you use.
You must install solara too because it is automatically imported when you import mesa.visualization.


You can verify that everything is installed correctly.
```bash
python tests/minimal.py
```
Or a more complete test:
```bash
python tests/with_model_params.py
```

### Repository structure

The repository contains multiplie folders.  
- All code is in the **mesa_graphics** folder.  
- The tests are python files that call our library. They are all in the **tests** folder.  
- In the **doc** folder, you have all the documentation files, used for new contributors, and to describe the design 
and implementation of the library. Some files were created for my internship.

Finally, there are some files in none of these folders. These files are here for users.


## Conception 

The class MesaGraphics is the starting point of the graphic interface. It starts automatically all the modules which 
will create the window, start the visualization, and start to take account of the user's inputs.

### High Level Architecture

MesaGraphics follow the **Model-View-Controller** (MVC) pattern. So, it has the three main classes:
- **Model**: Contains the user's Model, and some attributes.
- **View**: Creates the window, place all the UI elements onto the screen, and handle the logic to show them.
- **Controller**: Handles the user's inputs.

### High Level flow

You can see below a graphical representation of the high level flow.

![flow](block_diagram.png)

For better performances, we implemented multithreading.

The main thread is really lightweight. It handles the user's inputs, and draw onto the screen. This thread shall be 
really fast to have a responsive interface. It runs currently approximately at 1000 fps.

The worker thread performs all the computationally expensive operations. So, it generates the plots, and simulate the 
Model. These two operations can be arbitrarily expensive because the user can give custom plots and custom Model.

The multithreading can make a lot of subtle bugs really hard to debug. So, when you add code, pay attention to the 
following points:
- `View.draw` must not draw things depending on the user's Model state. It could draw the Model only half simulated, 
drawing a model state that never existed. If you want to draw things depending on the Model state, please start by 
rendering them in the `View.render` function, and then draw the rendered image. This solves the problem because the 
rendering function and the Model simulation function are in the same thread.
- In general, try using attributes in only one thread. Be careful when attributes are modified and used in 
different threads.
- Python use GIL: The Python Global Interpreter Lock or GIL, in simple words, is a mutex (or a lock) that allows only 
one thread to hold the control of the Python interpreter. So modifying an attribute in two different threads can be 
acceptable.


## More precise architecture

Below, the complete architecture

![architecture](MesaGraphics.png)

### Files

A quick explanation of what you can find in each file:
- **MesaGraphics.py**: The starting point of the application
- **Model.py**: There is the Model class. It is a class containing the user's defined Model class, and some other 
attributes.  
- **Controller.py**: There is the Controller layer, that's to say the Controller, the ButtonsController, and the 
  UserParamController.
- **View.py**: There is the View component. Where all the graphical elements are instantiated, and drawn.
- **UIElement.py**: There is all the different graphical elements. (Button, Rectangle, Slider, Checkbox, ...).

### Controller

All the events are handled by InputHandler. This class allows you to directly know if some key is pressed, held, or 
released.  
The Controller is divided into ButtonsController and UserParamController. The ButtonsController part is responsible for 
the Button actions, while the UserParamController is responsible for modifying the userParam values according to the 
user's inputs.

### UIElement

All the graphical elements are UIElements (except the components).
In the UIElement class, there is only the logic to draw them. The logic to interact with them is in the Controller part.

You can create UIElement through the `View.add_UIElement` function.
The order in which you create UIElements is meaningful. They are drawn in the same order.

If you want to create new graphical elements, you can create classes that inherit from UIElement (implementing draw).

### Interacting with buttons

Each Button has a name. This name can be the one chosen, or by default, if none is chosen, the text in it. Each name is 
guaranteed to be unique. If a duplicate name is provided, it is automatically modified. The ButtonsController part has 
a dictionary called `button_actions` associates each button name with the function that will be called once the 
button is pressed.

The ButtonsController will at each update see if the user clicks a button, and if so, he will execute the 
associated function.

If you want to add a button:
1. Create the button in View using the function `View.add_UIElement(Button, ...)`. For example, 
`View.add_UIElement(Button, pg.Vector2(0, 0), "hello world", self.fonts["basic15"], name="printHelloWorld")`
2. Be careful to give a new name. For clarity, I advise to give an explicit name, even if the name parameter is 
facultatif
3. In ButtonsController, associate to the name of the button the action it does when pressed. For example: 
`self.button_actions["printHelloWorld"] = lambda: print("HelloWorld")`

### Interacting with UserParam

Interacting with UserParam is pretty similar to interacting with buttons. Each UserParam has a name just as the buttons.
When the user change a UserParam value, the UserParamController calls a method of the UserParam to describe the change.
Finally, when the user re-instantiate the Model, the UserParamController iterates through all the UserParam to retrieve 
their values, and use them to instantiate the next model.


