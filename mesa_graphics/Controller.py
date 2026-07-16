import mesa.visualization

from .InputHandler import InputHandler
from .UIElement import Button, Slider, UserParam, Checkbox, Select, InputText, ScrollingSlider
from pygame import Vector2
from .Model import Model
from .View import View

from pygame import Vector2


class Controller:
    def __init__(self, model: Model, view: View, model_params=None):
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
        self.userParamController = UserParamController(model, view, self.inputHandler, model_params=model_params)
        self.buttonsController = ButtonsController(model, view, self.inputHandler, self.userParamController)
        self.anormal_termination = False

    def update(self):
        """
        This is the main function. It is called once per frame. It watches the new user inputs, and
        act responding to them.
        """
        self.update_counters()
        self.inputHandler.update()
        self._update_ui()
        if self.inputHandler.resize():
            self.view.resize(self.inputHandler.resize())
        self.scroll()

    def scroll(self):
        """
        This function checks if the user is scrolling, and scrolls depending on where the mouse is.
        If the mouse is in the left part of the screen, the user will scroll through the user parameters, and if the
        mouse is in the right part, the user will scroll through the components.
        """
        # If the mouse on the user parameters part of the screen
        if self.inputHandler.mouse_pos.x > 300 * self.view.userParamView.show_control_bar:
            self.view.scroll_page(Vector2(self.inputHandler.scroll_direction.x,
                                          -self.inputHandler.scroll_direction.y))
            self.view.userParamView.scroll_params(0)
        # If the mouse on the components part of the screen
        else:
            self.view.userParamView.scroll_params(-self.inputHandler.scroll_direction.y)

    def update_counters(self):
        """
        Every key has a counter, counting how many frame was the last modification. This function update this counters.
        """
        self.inputHandler.update_counters()

    def _update_ui(self):
        """ It updates all the UI, reacting to user's inputs: buttons and user parameters. """

        # Checks if the user focuses a specific UI element
        # If so, only this UI element is updated
        # Only Sliders, Selects, InputTexts can be focused
        if self.view.ui_focused is not None:
            self._update_single_ui(self.view.ui_focused, True)

        else:
            # updates each UI element
            for ui in self.view.ui_elements:
                self._update_single_ui(ui)

    def _update_single_ui(self, ui, focused=False):
        """ Updates a single UI element according to the user's inputs """

        # Asks the right controller's part to update the ui element
        if isinstance(ui, Button):
            self.buttonsController.update(ui)
        if isinstance(ui, UserParam):
            self.userParamController.update(ui, focused)

    @property
    def is_terminated(self):
        """ Get if user asked to close the window, and so, to end the visualization. """
        return self.inputHandler.quit or self.anormal_termination

    def terminate(self):
        """ This function is called when an error occurred, to stop the visualization. """
        self.anormal_termination = True


class UserParamController:
    def __init__(self, model: Model, view: View, inputHandler: InputHandler, model_params=None):
        """
        This class is responsible to update the user's params, according to the user's inputs.
        The user's params are the sliders, and buttons in the column, in the left part of the screen.
        """
        self.model = model
        self.view = view
        self.inputHandler = inputHandler

        # Stores the raw model parameter information.
        # For example, user can put something like : model_params = { "n": 3 }
        self.primitive_model_params = {}

        self.set_default_model_params(model_params)

    def set_default_model_params(self, model_params):
        """
        Puts in self.primitive_model_params the raw model parameter information.
        For example, user can put something like : model_params = { "n": 3 }
        So, self.primitive_model_params would be { "n": 3 }
        """

        # If the user gave no model_params, primitive_model_params remains empty
        if model_params is None:
            return

        # If model_params is not empty
        for param in model_params:

            # If the model_params[param] is a primitive value
            if not (isinstance(model_params[param], dict) or isinstance(model_params[param], mesa.visualization.Slider)):
                self.primitive_model_params[param] = model_params[param]

    def update(self, userParam: UserParam, focused=False):
        """
        Updates a single userParameter according to the user's inputs.

        :param userParam: The userParam to update
        :param focused: Boolean describing if the userParam is focused. If a userParam is focused, only this UI element
        is updated Only Sliders, Selects, InputTexts can be focused.
        """
        mousePos = self.inputHandler.mouse_pos

        if isinstance(userParam, Slider):
            userParam.hover = (userParam.pos.x <= mousePos.x <= userParam.pos.x + userParam.length and
                               userParam.pos.y - 5 <= mousePos.y <= userParam.pos.y + 5)
            if focused:
                # If it is focused, the user can continue changing the value on the slider, even if the mouse is not on
                # the slider. It is focused when the user is dragging it.
                userParam.hover = True

                # Stops to focus if the user stops to drag it
                if not self.inputHandler.holding("mouse_left"):
                    userParam.hover = False
                    self.view.ui_focused = None

            # If the user is dragging the slider.
            if userParam.hover and self.inputHandler.holding("mouse_left"):
                self.view.ui_focused = userParam

                # pos is the mouse position relatively to the slider between 0 and 1.
                # pos = 0 means value = minValue; pos = 1 means value = maxValue
                pos = (mousePos.x - userParam.pos.x) / userParam.length

                # The value of the parameter computed with a linear interpolation
                value = userParam.min + pos * (userParam.max - userParam.min)

                # Make value as the closest multiple of userParam.step
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

        elif isinstance(userParam, Select):
            if userParam.is_toggled:
                if self.inputHandler.pressed("mouse_left"):
                    # if the mouse is in the column of the userParam
                    if userParam.pos.x <= mousePos.x <= userParam.pos.x + userParam.toggle_size.x:
                        # i is the index of the choice on which is the mouse
                        i = int((mousePos.y - userParam.pos.y) // userParam.toggle_size.y)
                        if 0 <= i < len(userParam.values):
                            userParam.set_value(userParam.values[i])

                    userParam.is_toggled = False
                    self.view.ui_focused = None

            else:
                hover = (userParam.pos.x <= mousePos.x <= userParam.pos.x + userParam.size.x and
                         userParam.pos.y - 5 <= mousePos.y <= userParam.pos.y + userParam.size.y)
                if hover and self.inputHandler.pressed("mouse_left"):
                    userParam.is_toggled = True
                    self.view.ui_focused = userParam

        elif isinstance(userParam, InputText):
            if not userParam.is_focused:
                hover = (userParam.pos.x <= mousePos.x <= userParam.pos.x + userParam.size.x and
                         userParam.pos.y - 5 <= mousePos.y <= userParam.pos.y + userParam.size.y)
                if hover and self.inputHandler.pressed("mouse_left"):
                    userParam.is_focused = True
                    self.view.ui_focused = userParam
            else:
                # self.inputHandler.unicode has what has been written since the last frame
                for letter in self.inputHandler.unicode:
                    # \x08: BACKSPACE
                    # \x0d: ENTER
                    # \x7f: DELETE
                    # \x1f: ` (before becoming the true accent)
                    if letter not in "\x08\x0d\x7f\x1f":
                        userParam.write(letter)
                if self.inputHandler.pressed("BACKSPACE") or self.inputHandler.get_duration("BACKSPACE") > 50:
                    userParam.remove()
                if self.inputHandler.pressed("DELETE") or self.inputHandler.get_duration("DELETE") > 50:
                    userParam.suppr()
                if self.inputHandler.pressed("RIGHT") or self.inputHandler.get_duration("RIGHT") > 50:
                    userParam.move_cursor(1)
                if self.inputHandler.pressed("LEFT") or self.inputHandler.get_duration("LEFT") > 50:
                    userParam.move_cursor(-1)
                if self.inputHandler.pressed("mouse_left"):
                    userParam.is_focused = False
                    self.view.ui_focused = None

        elif isinstance(userParam, ScrollingSlider):
            if focused:
                userParam.move_pointer_pos(self.inputHandler.mouse_movement)
                if self.view.ui_focused == userParam and not self.inputHandler.holding("mouse_left"):
                    self.view.ui_focused = None
            else:
                userParam.hover = (userParam.pos.x <= mousePos.x <= userParam.pos.x + userParam.size.x and
                                   userParam.pos.y <= mousePos.y <= userParam.pos.y + userParam.size.y)
                pointer_pos = userParam.get_pointer_pos() - Vector2(2, 2)  # pointer top left corner
                hover_pointer = (userParam.hover and pointer_pos.x <= mousePos.x <= pointer_pos.x + userParam.pointer_size.x + 4
                                 and pointer_pos.y <= mousePos.y <= pointer_pos.y + userParam.pointer_size.y + 4)
                if self.inputHandler.pressed("mouse_left"):
                    if hover_pointer:
                        self.view.ui_focused = userParam
                    elif userParam.hover:
                        userParam.move_pointer_pos(self.inputHandler.mouse_pos -
                                                   (userParam.get_pointer_pos() + userParam.pointer_size / 2))

        else:
            raise NotImplementedError(f"There are no implementation for {type(userParam)}")
        if not userParam.model_param:
            self.model.notify_user_entries_change(userParam.name, userParam.value)

    def get_model_params(self):
        """
        Get the parameters to put in the user's Model we want to re-instantiate.
        """
        res = self.primitive_model_params.copy()
        # Get the value of each userParam
        for param in self.view.userParamView.userTweakableModelParams:
            res[param] = self.view.userParamView.userTweakableModelParams[param].value
        return res

    def get_method_params(self, method_name):
        res = {}
        # Get the value of each userParam which associated_method is the right method
        for param_name in self.view.userParamView.userTweakableEntries:
            param = self.view.userParamView.userTweakableEntries[param_name]
            if param.associated_method == method_name:
                res[param_name] = param.value
        return res


class ButtonsController:
    def __init__(self, model: Model, view: View, inputHandler: InputHandler, userParamController: UserParamController):
        """
        This class handles the logic behind the buttons.

        :param model: A Model instance that will be visualized. It is the MesaGraphic's Model, and not
        the user's on.
        :param view: The View class.
        :param inputHandler: The Controller's inputHandler, to access more easily the user's inputs.
        :param userParamController: The Controller's sliderController.
        """
        self.model = model
        self.view = view
        self.inputHandler = inputHandler
        self.userParamController = userParamController
        self.button_actions = {}
        self._initialize_button_actions()

    def _initialize_button_actions(self):
        """ Initialize the actions to apply when the user click on the buttons. """
        self._initialize_control_buttons()
        self._initialize_switch_page_buttons()
        self._initialize_method_call_buttons()

    def _initialize_control_buttons(self):
        """
        Initialize the actions of the 3 buttons: RESET, START/STOP, STEP
        This function defines the actions as functions
        """

        def step_action():
            """ Code to execute when the user clicks on the STEP button """
            self.model.mesa_model.step()

        def start_or_stop_action():
            """
            Code to execute when the user clicks on the START/STOP button. It reverts the model's is_playing flag and
            modify the text of the START/STOP button.
            """
            self.model.is_playing = not self.model.is_playing
            self.view.buttons["START/STOP"].modify_text(("START", "STOP")[self.model.is_playing], color=(255, 255, 255))

        def reset_action():
            """
            Code to execute when the user clicks on the RESET button. It re-instantiates the Model, and put the
            model's is_playing flag to False.
            """
            self.model.reset = True
            self.model.set_model_params(self.userParamController.get_model_params())
            if self.model.is_playing:
                start_or_stop_action()

        def toggle_or_untoggle_control_bar():
            """ Code to execute when the user clicks on the toggle/untoggle button (in top left of the screen) """
            self.view.userParamView.toggle_untoggle_control_bar()

        self.button_actions["STEP"] = step_action
        self.button_actions["START/STOP"] = start_or_stop_action
        self.button_actions["RESET"] = reset_action
        self.button_actions["remove control bar"] = toggle_or_untoggle_control_bar

    def _initialize_switch_page_buttons(self):
        """ Initialize the actions of the switching page buttons """

        # We use this weird thing of putting a function in a function in a function because if we make something like :
        # for i in range(...):
        #     def switch_page():
        #         self.view.switch_page(i)
        #     self.buttons_actions[...] = switch_page
        # It would use the latest i, and not a different i for each switch_page function.
        def switch_page(i):
            def res():
                self.view.switch_page(i)
            return res

        # We associate the function to each button
        for i in range(self.view.componentsView.min_page, self.view.componentsView.max_page+1):
            self.button_actions[f"PAGE {i}"] = switch_page(i)

    def _initialize_method_call_buttons(self):
        def action(method_name):
            def res():
                # Get the method named method_name as a function
                method = getattr(self.model.mesa_model, method_name)
                if method is None:  # If the method doesn't exist
                    raise RuntimeError(f"The method {method_name} doesn't exist")
                params = self.userParamController.get_method_params(method_name)
                method(**params)
            return res

        # Associate the function to each button which name starts with "method_call-"
        for button_name in self.view.buttons:
            button = self.view.buttons[button_name]
            if button.name[:12] == "method_call-":
                method_name = button.name[12:]
                self.button_actions[button.name] = action(method_name)

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
                self.button_actions[button.name]()  # Call the method associated with
            else:
                print(f"button {button.name} action has not been implemented")

