from mesa import * 

# Définition de la classe Voiture, qui hérite de la classe Agent de Mesa
class Voiture(Agent):
    # constructeur de la classe Voiture
    def __init__(self, model, vitesse_initiale, vitesse_maximum):
        super().__init__(model)
        self.vitesse = vitesse_initiale
        self.compteur = 0  # Compteur pour suivre la progression
        self.VMAX = vitesse_maximum  # Vitesse maximale avant de réinitialiser le compteur
        # on ajoute une mesure du temps pour faire le tour du circuit
        self.last_start = 0
        self.last_run_duration = 0

    # Boucle procédurale
    def step(self):
        # on avance
        self.compteur += self.vitesse
        if self.compteur >= self.VMAX:  # Modulo VMAX, on fait avancer la voiture
            self.compteur = self.compteur - self.VMAX
            self.avancer()
            # et on essaye d'accélérer
            self.accelerer()
        # si la vitesse est nulle, on essaye d'accélérer
        if self.vitesse == 0:
            self.accelerer()

    # Faire avancer la voiture d'une case vers la droite seulement si la case est libre
    def avancer(self):
        new_pos = self.prochaine_case()
        l = self.model.grid.get_cell_list_contents([new_pos])
        if len(l)==0:
            self.model.grid.move_agent(self, new_pos)
            # lorsqu'on change de case, si on revient au début, mettre à jour la durée du tour
            if new_pos[0] == 0:
                self.last_run_duration = self.model.steps - self.last_start
                self.last_start = self.model.steps
        else:
            # Si la case est occupée, on pile
            self.vitesse = 0
            self.compteur = 0

    # Tenter d'accélrer si la case d'après est encore libre
    def accelerer(self):
        new_pos = self.prochaine_case()
        l = self.model.grid.get_cell_list_contents([new_pos])
        if len(l)==0:
            # Si la case est libre, on accélère
            self.vitesse += 1
            if self.vitesse > self.VMAX:
                self.vitesse = self.VMAX

    # La grille ne faisant pas le modulo du tore, il faut le faire à la main
    def prochaine_case(self):
        if self.pos[0]+1 == self.model.grid.width:
            return (0, self.pos[1])
        else:
            return (self.pos[0] + 1, self.pos[1])

# calcule la moyenne des durée de tour d'un agent
def average_speed_turn(model):
    agent_run_durations = [agent.last_run_duration for agent in model.agents]
    s = sum(agent_run_durations)
    return len(agent_run_durations)/s if s>0 else 0

# Définition de la classe Route, qui hérite de la classe Model de Mesa
class Route(Model):
    # constructeur de la classe Route
    def __init__(self, N=1, taille=20, VMAX=5, seed=None):
        super().__init__(seed=seed)
        self.grid = space.MultiGrid(taille, 1, True)  # Création d'une grille 1D de taille spécifiée

        # Placement des N voitures : chaque voiture est placée sur une case différente
        for i in range(N):
            voiture = Voiture(self, 0, VMAX) # au début tout le monde est arrêté
            self.grid.place_agent(voiture, (i, 0))

        # On collecte à chaque tour la moyenne des durée du tour des voiture
        # et la vitesse courante de chaque voiture
        self.datacollector = DataCollector(
            model_reporters={"average_speed_run": average_speed_turn},
            agent_reporters={"Speed": "vitesse"}
        )
        self.datacollector.collect(self)

    # Méthode step pour la simulation
    def step(self):
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)
