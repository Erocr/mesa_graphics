from mesa_graphics.InputHandler import InputHandler
from mesa_graphics.UIElement import UIButton


class Controller:
    def __init__(self, model, view, model_params=None):
        self.inputHandler = InputHandler()
        self.model = model
        self.view = view
        self.buttonsController = ButtonsController(model, view, self.inputHandler)

    def update(self):
        self.inputHandler.update()
        self.update_ui()

    def update_ui(self):
        for ui in self.view.ui_elements:
            if isinstance(ui, UIButton):
                self.buttonsController.update(ui)


    @property
    def is_terminated(self):
        return self.inputHandler.quit


class ButtonsController:
    def __init__(self, model, view, inputHandler):
        self.model = model
        self.view = view
        self.inputHandler = inputHandler
        self.button_actions = {}
        self.initialize_button_actions()

    def initialize_button_actions(self):
        self._initialize_control_buttons()
        self._initialize_switch_page_buttons()

    def _initialize_control_buttons(self):
        def step_action():
            self.model.mesa_model.step()

        def start_or_stop_action():
            self.model.is_playing = not self.model.is_playing
            self.view.buttons["START/STOP"].modify_text(("START", "STOP")[self.model.is_playing])

        def reset_action():
            model = type(self.model.mesa_model)()
            self.model.mesa_model = model
            if self.model.is_playing:
                start_or_stop_action()

        self.button_actions["STEP"] = step_action
        self.button_actions["START/STOP"] = start_or_stop_action
        self.button_actions["RESET"] = reset_action

    def _initialize_switch_page_buttons(self):
        def switch_page(i):
            def res():
                self.view.page = i
            return res
        for i in range(self.view.min_page, self.view.max_page+1):
            self.button_actions[f"PAGE {i}"] = switch_page(i)

    def update(self, button):
        mouse_pos = self.inputHandler.mouse_pos
        button.hover = (button.pos.x <= mouse_pos.x <= button.pos.x + button.size.x and
                        button.pos.y <= mouse_pos.y <= button.pos.y + button.size.y)
        if button.hover and self.inputHandler.pressed("mouse_left"):
            if button.name in self.button_actions:
                self.button_actions[button.name]()
            else:
                print(f"button {button.name} action has not been implemented")



