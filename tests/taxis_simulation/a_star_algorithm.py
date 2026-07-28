import mesa.discrete_space
import heapq
import time


class CellDirection:
    """
    L'état d'une voiture est définie non seulement par sa position, mais aussi par sa direction.
    """
    def __init__(self, cell, direction):
        self.cell = cell
        self.direction = direction

    def __hash__(self):
        return hash((self.cell, self.direction))

    def __eq__(self, other):
        return isinstance(other, CellDirection) and self.cell == other.cell and self.direction == other.direction

    def __str__(self):
        return str(self.cell.position) + " " + str(self.direction)

    def __repr__(self):
        return str(self)


class AStarNode:
    def __init__(self, cost: float, heuristic: float, cell: mesa.discrete_space.Cell, direction):
        self.cost = cost
        self.heuristic = heuristic
        self.cell = cell
        self.direction = direction
        self.parent: CellDirection | None = None

    def __lt__(self, other):
        """
        Surcharge l'opérateur '<'
        Utile pour heapq
        """
        return self.heuristic - self.cost < other.heuristic - other.cost


def a_star(cell1: mesa.discrete_space.Cell, cell2: mesa.discrete_space.Cell, starting_direction, model):
    """
    Prend en paramètre les positions de deux points p1 et p2.
    Il renvoie le chemin pour aller de p1 à p2 trouvé utilisant l'algorithme A*
    """
    # closed_list est un dictionnaire qui associe aux noeuds déjà visités le noeud parent.
    closed_list: dict[CellDirection: CellDirection] = {}

    # open_list contient les cases à visiter
    # C'est une file prioritaire, on gère ça avec heapq
    open_list: list[AStarNode] = []

    # On ajoute l'élément de départ.
    # Il a un coût de 0, et l'heuristique est la distance à la case d'arrivée
    heapq.heappush(open_list, AStarNode(0, dist(cell1.position, cell2.position), cell1, starting_direction))

    start = time.time()
    while len(open_list) > 0:
        u_node = heapq.heappop(open_list)  # On prend l'élément à l'heuristique minimale

        # Si c'est la case d'arrivée, on a fini
        if u_node.cell.position[0] == cell2.position[0] and u_node.cell.position[1] == cell2.position[1]:
            closed_list[CellDirection(u_node.cell, u_node.direction)] = u_node.parent
            return reconstruct_path(closed_list, CellDirection(cell1, starting_direction),
                                    CellDirection(u_node.cell, u_node.direction))

        # On ajoute les voisins dans open_list
        for v in u_node.cell.neighborhood:
            # C'est le coût ajouté pour aller à la case v depuis u
            cost_add = cost_delta(u_node.cell, v, u_node.direction, model)
            if cost_add < 0:
                continue

            dir_ = compute_direction(u_node.cell, v)
            # Si v existe dans closed_list, alors il a déjà été visité : on ne le revisite pas
            if CellDirection(v, dir_) in closed_list:
                continue

            v_cost = u_node.cost + 1  # TODO: améliorer le coût pour qu'il prenne e compte la décélération quand on tourne

            # Cherche si v est déjà dans open_list.
            # Si c'est le cas, on met le noeud associé dans v_in_open_list
            v_in_open_list = search_cell(open_list, v, dir_)

            # On choisit ce chemin seulement s'il n'y a pas déjà un meilleur chemin
            if v_in_open_list is None or v_in_open_list.cost > v_cost:
                if v_in_open_list is not None:
                    # On détruit le noeud déjà existant
                    open_list.remove(v_in_open_list)
                    heapq.heapify(open_list)

                # On calcule le noeud à ajouter
                v_heuristic = v_cost + dist(cell2.position, v.position)
                v_direction = v.position[0] - u_node.cell.position[0], v.position[1] - u_node.cell.position[1]
                v_node = AStarNode(v_cost, v_heuristic, v, v_direction)
                v_node.parent = CellDirection(u_node.cell, u_node.direction)

                # On ajoute le noeud
                heapq.heappush(open_list, v_node)

        # On ajoute dans closed_list la case qu'on vient de visiter
        closed_list[CellDirection(u_node.cell, u_node.direction)] = u_node.parent

    raise RuntimeError(f"There is no path from {cell1.position} to {cell2.position}")


def reconstruct_path(closed_list, cell1: CellDirection, cell2: CellDirection):
    """ Reconstruit le chemin qui va de cell1 à cell2 par rapport au closed_list """
    # Dans closed_list, on associe les parents des cellules.
    # Donc, on retrouve les parents jusqu'à trouver cell1
    inverted_path = [cell2]
    while inverted_path[-1] != cell1:
        inverted_path.append(closed_list[inverted_path[-1]])

    inverted_path.reverse()
    return path_to_directions(inverted_path)


def path_to_directions(path: list[CellDirection]):
    """
    Transforme un chemin décrit par les positions et les directions que prend la voiture par une suite d'instruction.
    Les instructions sont une chaîne de caractère.
    Les instructions peuvent être 'f' : forward, 'l' : left, 'r' : right
    """
    currentDir = path[0].direction
    res = ""
    for cellDir in path[1:]:
        if cellDir.direction == currentDir:
            res += "f"
        elif cellDir.direction[0] == -currentDir[1] and cellDir.direction[1] == currentDir[0]:
            res += "l"
        elif cellDir.direction[0] == currentDir[1] and cellDir.direction[1] == -currentDir[0]:
            res += "r"
        else:
            raise RuntimeError("Sequence of directions not allowed")

        currentDir = cellDir.direction
    return res


def search_cell(open_list, searched_cell, direction) -> AStarNode | None:
    """
    Cherche une cellule dans open_list, s'il y en a plusieurs identiques, donne celle avec le coût minimal.
    S'il la trouve, renvoie le noeud associé, sinon renvoie None
    """
    for node in open_list:
        if node.cell == searched_cell and node.direction == direction:
            return node


def dist(p1, p2):
    """
    Calcule la distance infinie entre p1 et p2.
    On choisit la distance infinie car la grille est de Von Neumann (4 cases adjacentes)
    """
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def compute_direction(cell1, cell2):
    """ Calcule le vecteur qui va de cell1 à cell2 """
    return cell2.position[0] - cell1.position[0], cell2.position[1] - cell1.position[1]


def cost_delta(cell1, cell2, previous_direction, model):
    """
    Renvoie l'augmentation de coût pour aller de cell1 à cell2, avec cell1 et cell2 adjacentes.
    Si le coût est -1, alors il est impossible de passer par là.
    """
    # Si la case cell2 n'est pas de la route, la voiture ne peut pas y aller dessus
    if not model.is_road(cell2):
        return -1

    direction = compute_direction(cell1, cell2)
    dot_ = dot(direction, previous_direction)

    # Si le vecteur va dans le sens opposé, il ne peut pas y aller. Les voitures ne peuvent pas aller vers l'arrière.
    if dot_ < 0:
        return -1

    else:
        return 1  # TODO: le faire plus fin si jamais la voiture tourne


def dot(v1, v2):
    """ Calcul le produit scalaire entre deux vecteurs """
    return v1[0] * v2[0] + v1[1] * v2[1]
