from BasicCar import *
from tests.taxis_simulation.a_star_algorithm import find_final_direction


# Au vu de la construction de BasicCar, il n'y a que la fonction deliberate qui est à changer

class TwoPassengersCar(BasicCar):
    EPSILON = 3

    def __init__(self, model, cell, max_speed=5):
        super().__init__(model, cell, max_speed)
        self.transport = []
        self.static = False

    def two_passengers_proposition_accepted_deliberation(self, perception):
        if self.sent_proposition.cell == self.cell:
            self.transport.append(self.sent_proposition)
            self.sent_proposition = None
            self.transport[-1].transported_by(self)
            self.state = BasicCar.TRANSPORTING

        # Si la personne disparaît
        elif self.sent_proposition in perception[5]:
            # Oublie la personne
            self.sent_proposition = None
            self.follow_path = False
            # Rentre en état IDLE
            self.state = BasicCar.IDLE

        return []

    def two_passengers_transport_deliberation(self, perception):
        actions = self.basic_transport_deliberation(perception)

        if len(self.transport) == 1 and self.sent_proposition is not None and self.static:
            self.sent_proposition_timer += 1
            if perception[4] is not None and perception[4]:
                self.path = self.route_computed
                self.follow_path = True
                self.static = False
            elif (perception[4] is not None and not perception[4]) \
                    or self.sent_proposition_timer > Passenger.TIME_WAIT_BEFORE_ACCEPT + 1:
                self.route_computed = ""
                self.sent_proposition = None
                self.follow_path = True
                self.static = False
        if len(self.transport) == 1 and self.sent_proposition is not None:
            if self.cell == self.sent_proposition.cell:
                self.transport.append(self.sent_proposition)
                self.sent_proposition = None
                self.static = False
                self.transport[-1].transported_by(self)

        if len(self.transport) == 1:
            # Si la personne disparait
            if self.transport[0] in perception[5]:
                # Oublie la personne
                self.transport = []
                self.follow_path = False
                # Rentre en état IDLE
                self.state = BasicCar.IDLE
                self.static = False

            # Si jamais son chemin est vide, il le recalcule
            elif self.path == "":
                self.path = a_star(self.cell, self.transport[0].goal, self.direction, self.model)

        elif len(self.transport) == 2:
            if self.transport[0] in perception[5]:
                self.transport.pop(0)

            elif self.transport[1] in perception[5]:
                self.transport.pop(1)

            # Si jamais son chemin est vide, il le recalcule
            elif self.path == "":
                goal1 = self.transport[0].goal
                path1 = a_star(self.cell, goal1, self.direction, self.model)
                dir1 = find_final_direction(self.direction, path1)
                path2 = a_star(goal1, self.transport[1].goal, dir1, self.model)
                self.path = path1 + path2

        # Il peut potentiellement ne plus être dans l'état TRANSPORT
        # S'il peut prendre quelqu'un d'autre
        if len(self.transport) == 1 and self.sent_proposition is None:
            self.route_computed = ""
            best_passenger = None
            discussion_nb = 0
            best_detour = 100000
            for proposition in perception[3]:
                passenger, pos, passenger_goal, disc_nb = proposition

                # Calcule le détour
                # le premier passager va vers A1 (arrivée 1), le deuxième va de D2 à A2, et la voiture est à V
                # Alors les chemins possibles sont V->D2->A1->A2 (path1) ou V->D2->A2->A1 (path2)
                # ou V->A1->D2->A2 (pas très intéressant donc ignoré)
                A1 = self.goal
                D2 = self.model.grid.find_nearest_cell(pos)
                A2 = self.model.grid.find_nearest_cell(passenger_goal)
                V = self.cell

                V_to_D2 = a_star(V, D2, self.direction, self.model)
                dir2 = find_final_direction(self.direction, V_to_D2)
                D2_to_A1 = a_star(D2, A1, dir2, self.model)
                dir3 = find_final_direction(dir2, D2_to_A1)
                A1_to_A2 = a_star(A1, A2, dir3, self.model)

                path1 = V_to_D2 + D2_to_A1 + A1_to_A2

                D2_to_A2 = a_star(D2, A2, dir2, self.model)
                dir3 = find_final_direction(dir2, D2_to_A2)
                A2_to_A1 = a_star(A2, A1, dir3, self.model)

                path2 = V_to_D2 + D2_to_A2 + A2_to_A1

                best_path = min(path1, path2, key=lambda x: len(x))

                # self.path est le chemin pour envoyer le premier passager, et D2_to_A2 est le chemin pour envoyer le second
                # C'est le chemin minimal
                length_detour = len(best_path) - len(self.path) - len(D2_to_A2)

                if length_detour < self.EPSILON and length_detour < best_detour:
                    self.route_computed = best_path
                    best_passenger = passenger
                    discussion_nb = disc_nb
                    best_detour = length_detour

            if best_passenger is not None:
                # La distance est la taille du détour
                actions.append((Message(Message.INFORMATIF,
                                        f"distance {len(self.route_computed) - len(self.path)}",
                                        discussion_nb),
                                best_passenger))
                self.sent_proposition = best_passenger
                self.discussion_nb = discussion_nb
                self.static = True
                self.sent_proposition_timer = 0

        return actions

    def deliberate(self, perception: list) -> list:
        actions = []

        # S'il n'a rien à faire
        if self.state == BasicCar.IDLE:
            actions += self.basic_idle_deliberation(perception)

        elif self.state == BasicCar.SENT_PROPOSITION:
            actions += self.basic_sent_proposition_deliberation(perception)

        elif self.state == BasicCar.PROPOSITION_ACCEPTED:
            actions += self.two_passengers_proposition_accepted_deliberation(perception)
            # TODO : choisir pendant qu'il va voir quelqu'un d'aller voir qqn d'autre

        elif self.state == BasicCar.TRANSPORTING:
            actions += self.two_passengers_transport_deliberation(perception)

        if not self.static:
            if self.follow_path:
                return self.deliberation_with_path(perception) + actions
            else:
                return self.deliberation_without_path(perception) + actions
        else:
            return [(0, 0)] + actions
