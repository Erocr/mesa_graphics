from time import time


class Model:
    def __init__(self, mesa_model):
        self.mesa_model = mesa_model
        self.is_playing = False
        self.debug_infos = {}
        self.debug = False

    def update(self):
        start = time()
        if self.is_playing:
            self.mesa_model.step()
        self.debug_infos["model_time"] = time() - start
