from time import time
from typing import Any

from mesa import Model as MesaModel

NOT_RESETTING = 0
USER_ASK_RESET = 1
RESET_MODEL = 2


class Model:
    def __init__(self, mesa_model: MesaModel, play_interval: int, render_interval: int):
        """
        This is the MesaGraphics Model. It has the user's Model, and add some stuff, useful for viewing, and
        interacting with the user's Model.

        :param mesa_model: The user's Model.
        """
        self.mesa_model = mesa_model
        self.is_playing = False
        self.play_interval = play_interval
        self.render_interval = render_interval
        self.reset = NOT_RESETTING
        self.model_params = None

    def update(self):
        """ This function is called once per frame. It updates the user's Model if it is running. """
        if self.reset == USER_ASK_RESET:
            self.mesa_model = type(self.mesa_model)(**self.model_params)
            self.reset = RESET_MODEL
        else:
            if self.is_playing:
                # We don't need a deepcopy because only view.render() use mesa_model (which is in the same thread)
                next_mesa_model = self.mesa_model
                for i in range(self.render_interval):
                    next_mesa_model.step()
                self.mesa_model = next_mesa_model

    def notify_user_entries_change(self, entry_name: str, new_value: Any):
        """
        This function is called by the UserParamController. It is used to notify to the Model that the user has
        modified an option.

        :param entry_name: The name of the userParam from which we got this information.
        :param new_value: The value the user wrote in.
        """
        if entry_name == "play_interval":
            self.play_interval = new_value
        elif entry_name == "render_interval":
            self.render_interval = new_value

    def set_model_params(self, new_model_params: dict):
        """
        Set the parameters for the Model that the player will re-instantiate.

        :param new_model_params: The model parameters and their values
        """
        self.model_params = new_model_params
