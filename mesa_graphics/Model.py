class Model:
    def __init__(self, mesa_model):
        self.mesa_model = mesa_model
        self.is_playing = False

    def update(self):
        if self.is_playing:
            self.mesa_model.step()