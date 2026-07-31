from BasicCar import *


# Au vu de la construction de BasicCar, il n'y a que la fonction deliberate qui est à changer

class TwoPassengersCar(BasicCar):

    EPSILON = 100
    def __init__(self, model, cell, max_speed=5):
        super().__init__(model, cell, max_speed)
        self.transport = []
        self.path_if_accepted = None

    def two_passengers_transport_deliberation(self, perception):
        self.basic_transport_deliberation(perception)

    def deliberate(self, perception: list) -> list:
        actions = []

        # S'il n'a rien à faire
        if self.state == BasicCar.IDLE:
            actions += self.basic_idle_deliberation(perception)

        elif self.state == BasicCar.SENT_PROPOSITION:
            actions += self.basic_sent_proposition_deliberation(perception)

        elif self.state == BasicCar.PROPOSITION_ACCEPTED:
            actions += self.basic_proposition_accepted_deliberation(perception)

        elif self.state == BasicCar.TRANSPORTING:
            actions += self.basic_transport_deliberation(perception)

        if not self.state == BasicCar.IDLE:
            return self.deliberation_with_path(perception) + actions
        else:
            return self.deliberation_without_path(perception) + actions

