from mesa_graphics.InputHandler import InputHandler


class Controller:
    def __init__(self):
        self.inputHandler = InputHandler()

    def update(self):
        self.inputHandler.update()

    @property
    def is_terminated(self):
        return self.inputHandler.quit
