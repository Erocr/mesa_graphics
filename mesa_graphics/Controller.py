from mesa_graphics.InputHandler import InputHandler
from mesa_graphics.UIElement import UIButton, UISlider


class Controller:
    def __init__(self, model, view):
        self.inputHandler = InputHandler()
        self.model = model
        self.view = view
        self.sliderController = SliderController(model, view, self.inputHandler)
        self.buttonsController = ButtonsController(model, view, self.inputHandler, self.sliderController)

    def update(self):
        self.inputHandler.update()
        self.update_ui()

    def update_ui(self):
        for ui in self.view.ui_elements:
            if isinstance(ui, UIButton):
                self.buttonsController.update(ui)
            if isinstance(ui, UISlider):
                self.sliderController.update(ui)

    @property
    def is_terminated(self):
        return self.inputHandler.quit


class ButtonsController:
    def __init__(self, model, view, inputHandler, sliderController):
        self.model = model
        self.view = view
        self.inputHandler = inputHandler
        self.sliderController = sliderController
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
            params = self.sliderController.get_model_params()
            model = type(self.model.mesa_model)(**params)
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


class SliderController:
    def __init__(self, model, view, inputHandler):
        self.model = model
        self.view = view
        self.inputHandler = inputHandler

    def update(self, slider):
        mousePos = self.inputHandler.mouse_pos
        slider.hover = (slider.pos.x <= mousePos.x <= slider.pos.x + slider.length and
                        slider.pos.y - 5 <= mousePos.y <= slider.pos.y + 5)
        if slider.hover and self.inputHandler.holding("mouse_left"):
            pos = (mousePos.x - slider.pos.x) / slider.length
            value = slider.min + pos * (slider.max - slider.min)
            if slider.type == "SliderInt":
                value = round(value)
            slider.set_value(value)

    def get_model_params(self):
        res = {}
        for param in self.view.sliders:
            res[param] = self.view.sliders[param].value
        return res

