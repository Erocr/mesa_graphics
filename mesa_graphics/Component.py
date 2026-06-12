class Component:
    def __init__(self, mesa_model, component_func):
        self.mesa_model = mesa_model
        self.component_func = component_func
        self.image = None

    def render(self):
        self.image = self.component_func(self.mesa_model)
        if self.image is None:
            raise RuntimeError("The component didn't return anything. "
                               "Hint: maybe you forgot to to put the return keyword at the end of the function.")
