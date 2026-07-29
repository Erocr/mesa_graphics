from typing import Iterable

import mesa.discrete_space


class Message:
    REQUEST = 1
    REQUEST_DO = 2
    INFORMATIF = 3

    """
    Un message est ce qui va être envoyé avec la messagerie.
    Un message contient un performatif, un contenu, et de manière facultative un numéro de discussion
    (0 si aucune discussion particulière)
    """
    def __init__(self, performatif: int, content: str, discussion_nb=0):
        self.performatif = performatif
        self.content = content
        self.discussion_nb = discussion_nb



BROAD_CAST = 0
CARS = 1
PASSENGERS = 2
