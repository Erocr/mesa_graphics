from time import time


class Model:
    def __init__(self, mesa_model):
        """
        This is the MesaGraphics Model. It has the user's Model, and add some stuff, useful for viewing, and
        interacting with the user's Model.

        :param mesa_model: The user's Model.
        """
        self.mesa_model = mesa_model
        self.is_playing = False
        self.debug_infos = {}
        self.debug = False

    def update(self):
        """ This function is called once per frame. It updates the user's Model if it is running. """
        start = time()
        if self.is_playing:
            self.mesa_model.step()
        self.debug_infos["model_time"] = time() - start
