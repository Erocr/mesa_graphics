from mesa_graphics.InputHandler import InputHandler


class Controller:
    def __init__(self, model, view):
        self.inputHandler = InputHandler()
        self.model = model
        self.view = view

    def update(self):
        self.inputHandler.update()

    @property
    def is_terminated(self):
        return self.inputHandler.quit
