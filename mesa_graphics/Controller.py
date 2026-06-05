from mesa_graphics.InputHandler import InputHandler
from mesa_graphics.UIElement import UIButton


class Controller:
    def __init__(self, model, view):
        self.inputHandler = InputHandler()
        self.model = model
        self.view = view

    def update(self):
        self.inputHandler.update()
        self.update_ui()

    def update_ui(self):
        for ui in self.view.ui_elements:
            if isinstance(ui, UIButton):
                self._update_button(ui)

    def _update_button(self, button):
        mouse_pos = self.inputHandler.mouse_pos
        button.hover = (button.pos.x <= mouse_pos.x <= button.pos.x + button.size.x and
                        button.pos.y <= mouse_pos.y <= button.pos.y + button.size.y)
        if button.hover and self.inputHandler.pressed("mouse_left"):
            button.action()

    @property
    def is_terminated(self):
        return self.inputHandler.quit
