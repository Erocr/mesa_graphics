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


class Messaging:
    """
    Une messagerie (Messaging) est un objet qui peut envoyer des messages aux objets.
    Il a une liste de receveurs, et lorsque quelqu'un envoie un message, tous les receveurs reçoivent ce message.
    Si ce message leur est attribué, ils pourront l'utiliser, sinon, il sera ignoré.
    """
    MAX_DISCUSSION_NB = 255

    def __init__(self):
        self.receivers = []
        self.max_discussion_nb = 0

    def add_receiver(self, receiver):
        self.receivers.append(receiver)

    def remove_receiver(self, receiver):
        self.receivers.remove(receiver)

    def notify(self, message: Message, sender):
        """ Send the message to every receiver """
        assert 0 <= message.discussion_nb <= Messaging.MAX_DISCUSSION_NB
        self.max_discussion_nb = max(message.discussion_nb, self.max_discussion_nb)
        for receiver in self.receivers:
            receiver.notify(message, sender)

    def notify_specific(self, message: Message, sender, receiver):
        receiver.notify(message, sender)

    def get_new_discussion_nb(self):
        return (self.max_discussion_nb % 255) + 1
