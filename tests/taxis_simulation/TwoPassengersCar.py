from BasicCar import *


class TwoPassengersCar(BasicCar):
    def __init__(self, model, cell, max_speed=5):
        super().__init__(model, cell, max_speed)