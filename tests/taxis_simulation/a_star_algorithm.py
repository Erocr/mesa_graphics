import mesa.discrete_space
import heapq
import time
from math import sqrt


class AStarNode:
    def __init__(self, cost, heuristic, cell):
        self.cost = cost
        self.heuristic = heuristic
        self.cell = cell

    def __lt__(self, other):
        return self.heuristic < other.heuristic


def a_star(cell1: mesa.discrete_space.Cell, cell2: mesa.discrete_space.Cell):
    """
    Prend en paramètre les positions de deux points p1 et p2.
    Il renvoie le chemin pour aller de p1 à p2 trouvé utilisant l'algorithme A*
    """
    # closed_list associe aux cases déjà visitées le coût pour aller à cette case
    closed_list: dict[AStarNode: int] = {}

    # open_list contient les cases à visiter
    # C'est une file prioritaire, on va gérer ça avec heapq
    open_list: list[AStarNode] = []
    cost = 0  # Le coût pour aller de p1 au point initial
    heuristic = cost + dist(cell1.position, cell2.position)
    heapq.heappush(open_list, AStarNode(cost, heuristic, cell1))
    # On met heuristique d'abord, car heapq utilise le premier élément du tuple pour faire ses comparaisons

    start = time.time()
    # TODO: ne prend pas en compte les directions
    while len(open_list) > 0:
        u_node = heapq.heappop(open_list)  # On prend l'élément à l'heuristique minimale

        # Si c'est la case d'arrivée, on a fini
        if u_node.cell.position[0] == cell2.position[0] and u_node.cell.position[1] == cell2.position[1]:
            print(f"found in {time.time() - start}s")
            closed_list[u_node.cell] = u_node.cost
            return reconstruct_path(closed_list, cell1, cell2)

        # On ajoute les voisins dans open_list
        for v in u_node.cell.neighborhood:
            # Si v existe dans closed_list, alors il a déjà été visité : on ne le revisite pas
            if v in closed_list:
                continue

            v_cost = u_node.cost + 1  # TODO: améliorer le coût pour qu'il prenne e compte la décélération quand on tourne
            v_in_open_list = search_cell(open_list, v)

            # Si v est dans open_list avec un coût plus bas, alors il y a un chemin plus rapide qui va jusqu'à ce
            # noeud : on choisit ce chemin, pas le nouveau
            if v_in_open_list is None or v_in_open_list.cost > v_cost:
                # On calcule le noeud
                v_heuristic = v_cost + dist(cell2.position, v.position)
                v_node = AStarNode(v_cost, v_heuristic, v)

                # On ajoute le noeud
                heapq.heappush(open_list, v_node)

        # On ajoute dans closed_list la case qu'on vient de visiter
        closed_list[u_node.cell] = u_node.cost

    raise RuntimeError(f"There is no path from {cell1.position} to {cell2.position}")


def reconstruct_path(closed_list, cell1, cell2):
    """ Reconstruit le chemin qui va de cell1 à cell2 par rapport au closed_list """
    # Insert à la première place est plus long qu'à la dernière.
    # Donc, on le crée à l'envers, et on retourne la liste à la fin.
    inverted_path = [cell2]
    while inverted_path[-1] != cell1:
        current_cell = inverted_path[-1]
        for v in current_cell.neighborhood:
            if v in closed_list and closed_list[v] == closed_list[current_cell] - 1:
                inverted_path.append(v)
                break
        # S'il n'y a pas eu de break dans la boucle for
        else:
            inverted_path.reverse()
            raise RuntimeError(f"Could not reconstruct the path. Path found so far : {inverted_path}")

    inverted_path.reverse()
    return inverted_path


def search_cell(open_list, searched_cell) -> AStarNode | None:
    """
    Cherche une cellule dans open_list.
    S'il la trouve, renvoie le noeud associé, sinon renvoie None
    """
    for node in open_list:
        if node.cell == searched_cell:
            return node
    return None


def dist(p1, p2):
    """ Calcule la distance euclidienne entre p1 et p2 """
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
