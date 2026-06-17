from time import time


class Model:
    def __init__(self, mesa_model, play_interval, render_interval):
        """
        This is the MesaGraphics Model. It has the user's Model, and add some stuff, useful for viewing, and
        interacting with the user's Model.

        :param mesa_model: The user's Model.
        """
        self.mesa_model = mesa_model
        self.is_playing = False
        self.debug_infos = {}
        self.debug = False
        self.play_interval = play_interval
        self.render_interval = render_interval
        self.reset = False
        self.model_params = None

    def update(self):
        """ This function is called once per frame. It updates the user's Model if it is running. """
        start = time()
        if self.reset:
            self.mesa_model = type(self.mesa_model)(**self.model_params)
            self.reset = False
        else:
            if self.is_playing:
                # We don't need a deepcopy because only view.render() which is in the same thread use mesa_model
                next_mesa_model = self.mesa_model
                for i in range(self.render_interval):
                    next_mesa_model.step()
                self.mesa_model = next_mesa_model
        self.debug_infos["model_time"] = time() - start

    def notify_user_entries_change(self, entry_name, new_value):
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

    def set_model_params(self, new_model_params):
        """
        Set the parameters for the Model that the player will re-instantiate.

        :param new_model_params:
        """
        self.model_params = new_model_params
