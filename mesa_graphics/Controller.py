from .InputHandler import InputHandler
from .UIElement import Button, Slider, UserParam, Checkbox
from pygame import K_d
from .Model import Model
from .View import View


class Controller:
    def __init__(self, model: Model, view: View):
        """ Controller class
        /!\\ The user must not use this class, use MesaGraphics instead /!\\

        This class contains all the logic on how to handle the user inputs. It handles all the logic behind
        buttons and behind sliders.

        :param model: A Model instance that will be visualized. It is the MesaGraphic's Model, and not
        the user's one.
        :param view: The View class.
        """
        self.inputHandler = InputHandler()
        self.model = model
        self.view = view
        self.userParamController = UserParamController(model, view, self.inputHandler)
        self.buttonsController = ButtonsController(model, view, self.inputHandler, self.userParamController)

    def update(self):
        """
        This is the main function. It is called once per frame. It watches the new user inputs, and
        act responding to them.
        """
        self.update_counters()
        self.inputHandler.update()
        self._update_ui()
        if self.inputHandler.pressed(K_d):
            self.model.debug = not self.model.debug
        self.view.scroll(-self.inputHandler.scroll_direction.y)

    def update_counters(self):
        """
        Every key has a counter, counting how many frame was the last modification. This function update this counters.
        """
        self.inputHandler.update_counters()

    def _update_ui(self):
        """ It updates all the UI, reacting to user's inputs: buttons and sliders. """
        if self.view.ui_focused is not None:
            self._update_single_ui(self.view.ui_focused, True)
        else:
            for ui in self.view.ui_elements:
                self._update_single_ui(ui)

    def _update_single_ui(self, ui, focused=False):
        if isinstance(ui, Button):
            self.buttonsController.update(ui)
        if isinstance(ui, UserParam):
            self.userParamController.update(ui, focused)

    @property
    def is_terminated(self):
        """ Get if user asked to close the window, and so, to end the visualization. """
        return self.inputHandler.quit


class UserParamController:
    def __init__(self, model: Model, view: View, inputHandler: InputHandler):
        """
        This class is responsible to update the user's params, according to the user's inputs.
        The user's params are the sliders, and buttons in the column, in the left part of the screen.
        """
        self.model = model
        self.view = view
        self.inputHandler = inputHandler

    def update(self, userParam: UserParam, focused=False):
        """
        Updates a userParameter. Check if it must be changed, and if so, it calls the method in the userParam to make
        the change.
        :param userParam: The userParam to update
        :return:
        """
        mousePos = self.inputHandler.mouse_pos
        if isinstance(userParam, Slider):
            userParam.hover = (userParam.pos.x <= mousePos.x <= userParam.pos.x + userParam.length and
                               userParam.pos.y - 5 <= mousePos.y <= userParam.pos.y + 5)
            if focused:
                userParam.hover = True
                if not self.inputHandler.holding("mouse_left"):
                    userParam.hover = False
                    self.view.ui_focused = None
            if userParam.hover and self.inputHandler.holding("mouse_left"):
                self.view.ui_focused = userParam
                pos = (mousePos.x - userParam.pos.x) / userParam.length
                value = userParam.min + pos * (userParam.max - userParam.min)
                d, m = divmod(value, userParam.step)
                value = userParam.step * (d + (m > userParam.step * 0.5))
                if userParam.type == "SliderInt":
                    value = round(value)

                userParam.set_value(value)
        elif isinstance(userParam, Checkbox):
            hover = (userParam.pos.x <= mousePos.x <= userParam.pos.x + Checkbox.SIZE.x and
                     userParam.pos.y - 5 <= mousePos.y <= userParam.pos.y + Checkbox.SIZE.y)
            if hover and self.inputHandler.pressed("mouse_left"):
                userParam.switch()
        else:
            raise NotImplementedError()
        if not userParam.model_param:
            self.model.notify_user_entries_change(userParam.name, userParam.value)

    def get_model_params(self):
        """
        Get the parameters to put in the user's Model we want to re-instantiate.
        """
        res = {}
        for param in self.view.userTweakableModelParams:
            res[param] = self.view.userTweakableModelParams[param].value
        return res


class ButtonsController:
    def __init__(self, model: Model, view: View, inputHandler: InputHandler, sliderController: UserParamController):
        """
        This class handles the logic behind the buttons.

        :param model: A Model instance that will be visualized. It is the MesaGraphic's Model, and not
        the user's on.
        :param view: The View class.
        :param inputHandler: The Controller's inputHandler, to access more easily the user's inputs.
        :param sliderController: The Controller's sliderController.
        """
        self.model = model
        self.view = view
        self.inputHandler = inputHandler
        self.userParamController = sliderController
        self.button_actions = {}
        self._initialize_button_actions()

    def _initialize_button_actions(self):
        """ Initialize the actions to apply when the user click on the buttons. """
        self._initialize_control_buttons()
        self._initialize_switch_page_buttons()

    def _initialize_control_buttons(self):
        """ Initialize the actions of the 3 buttons: RESET, START/STOP, STEP """
        def step_action():
            self.model.mesa_model.step()

        def start_or_stop_action():
            self.model.is_playing = not self.model.is_playing
            self.view.buttons["START/STOP"].modify_text(("START", "STOP")[self.model.is_playing])

        def reset_action():
            self.model.reset = True
            self.model.set_model_params(self.userParamController.get_model_params())
            if self.model.is_playing:
                start_or_stop_action()

        def toggle_or_untoggle_control_bar():
            self.view.toggle_untoggle_control_bar()

        self.button_actions["STEP"] = step_action
        self.button_actions["START/STOP"] = start_or_stop_action
        self.button_actions["RESET"] = reset_action
        self.button_actions["remove control bar"] = toggle_or_untoggle_control_bar

    def _initialize_switch_page_buttons(self):
        """ Initialize the actions of the switching page buttons """
        def switch_page(i):
            def res():
                self.view.switch_page(i)
            return res
        for i in range(self.view.min_page, self.view.max_page+1):
            self.button_actions[f"PAGE {i}"] = switch_page(i)

    def update(self, button: Button):
        """
        This is the main function. It is called once per frame. It watches if the mouse hovers a button,
        and apply the action associated to the button if user clicks on it.
        """
        mouse_pos = self.inputHandler.mouse_pos
        button.hover = (button.pos.x <= mouse_pos.x <= button.pos.x + button.size.x and
                        button.pos.y <= mouse_pos.y <= button.pos.y + button.size.y)
        if button.hover and self.inputHandler.pressed("mouse_left") and not button.locked:
            if button.name in self.button_actions:
                self.button_actions[button.name]()
            else:
                print(f"button {button.name} action has not been implemented")

