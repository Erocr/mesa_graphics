class Component:
    def __init__(self, model, component_func):
        self.model = model
        self.component_func = component_func
        self.image = None

    def render(self):
        self.image = self.component_func(self.model.mesa_model)
        if self.image is None:
            raise RuntimeError("The component didn't return anything. "
                               "Hint: maybe you forgot to to put the return keyword at the end of the function.")
