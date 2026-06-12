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

    def update(self):
        """ This function is called once per frame. It updates the user's Model if it is running. """
        start = time()
        for i in range(self.render_interval):
            if self.is_playing:
                self.mesa_model.step()
        self.debug_infos["model_time"] = time() - start

    def notify_user_entries_change(self, entry_name, new_value):
        if entry_name == "play_interval":
            self.play_interval = new_value
        elif entry_name == "render_interval":
            self.render_interval = new_value
