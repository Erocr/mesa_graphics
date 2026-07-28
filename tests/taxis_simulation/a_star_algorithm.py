import mesa.discrete_space
import heapq
import time
from math import sqrt


class AStarNode:
    def __init__(self, cost, heuristic, cell):
        self.cost = cost
        self.heuristic = heuristic
        self.cell = cell
        self.parent: mesa.discrete_space.Cell | None = None

    def __lt__(self, other):
        """
        Surcharge l'opérateur <
        Utile pour heapq
        """
        return self.heuristic - self.cost < other.heuristic - other.cost


def a_star(cell1: mesa.discrete_space.Cell, cell2: mesa.discrete_space.Cell):
    """
    Prend en paramètre les positions de deux points p1 et p2.
    Il renvoie le chemin pour aller de p1 à p2 trouvé utilisant l'algorithme A*
    """
    # closed_list est un dictionnaire qui associe aux noeuds déjà visités le noeud parent.
    closed_list: dict[mesa.discrete_space.Cell: mesa.discrete_space.Cell] = {}

    # open_list contient les cases à visiter
    # C'est une file prioritaire, on gère ça avec heapq
    open_list: list[AStarNode] = []

    # On ajoute l'élément de départ.
    # Il a un coût de 0, et l'heuristique est la distance à la case d'arrivée
    heapq.heappush(open_list, AStarNode(0, dist(cell1.position, cell2.position), cell1))

    start = time.time()
    # TODO: ne prend pas en compte les directions
    while len(open_list) > 0:
        u_node = heapq.heappop(open_list)  # On prend l'élément à l'heuristique minimale

        # Si c'est la case d'arrivée, on a fini
        if u_node.cell.position[0] == cell2.position[0] and u_node.cell.position[1] == cell2.position[1]:
            print(f"found in {time.time() - start}s visiting {len(closed_list)} cells")
            closed_list[u_node.cell] = u_node.parent
            return reconstruct_path(closed_list, cell1, cell2)

        # On ajoute les voisins dans open_list
        for v in u_node.cell.neighborhood:
            # Si v existe dans closed_list, alors il a déjà été visité : on ne le revisite pas
            if v in closed_list:
                continue

            v_cost = u_node.cost + 1  # TODO: améliorer le coût pour qu'il prenne e compte la décélération quand on tourne

            # Cherche si v est déjà dans open_list.
            # Si c'est le cas, on met le noeud associé dans v_in_open_list
            v_in_open_list = search_cell(open_list, v)

            # On choisit ce chemin seulement s'il n'y a pas déjà un meilleur chemin
            if v_in_open_list is None or v_in_open_list.cost > v_cost:
                if v_in_open_list is not None:
                    # On détruit le noeud déjà existant
                    open_list.remove(v_in_open_list)
                    heapq.heapify(open_list)

                # On calcule le noeud à ajouter
                v_heuristic = v_cost + dist(cell2.position, v.position)
                v_node = AStarNode(v_cost, v_heuristic, v)
                v_node.parent = u_node.cell

                # On ajoute le noeud
                heapq.heappush(open_list, v_node)

        # On ajoute dans closed_list la case qu'on vient de visiter
        closed_list[u_node.cell] = u_node.parent

    raise RuntimeError(f"There is no path from {cell1.position} to {cell2.position}")


def reconstruct_path(closed_list, cell1, cell2):
    """ Reconstruit le chemin qui va de cell1 à cell2 par rapport au closed_list """
    # Dans closed_list, on associe les parents des cellules.
    # Donc, on retrouve les parents jusqu'à trouver cell1
    inverted_path = [cell2]
    while inverted_path[-1] != cell1:
        inverted_path.append(closed_list[inverted_path[-1]])

    inverted_path.reverse()
    return inverted_path


def search_cell(open_list, searched_cell) -> AStarNode | None:
    """
    Cherche une cellule dans open_list, s'il y en a plusieurs identiques, donne celle avec le coût minimal.
    S'il la trouve, renvoie le noeud associé, sinon renvoie None
    """
    for node in open_list:
        if node.cell == searched_cell:
            return node


def dist(p1, p2):
    """
    Calcule la distance infinie entre p1 et p2.
    On choisit la distance infinie car la grille est de Von Neumann (4 cases adjacentes)
    """
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
