import mesa.discrete_space


class Message:
    """
    Un message est ce qui va être envoyé avec la messagerie.
    Un message contient un performatif, un contenu, et de manière facultative un numéro de discussion
    (0 si aucune discussion particulière)
    """
    def __init__(self, performatif, content, discussion_nb=0):
        self.performatif = performatif
        self.content = content
        self.discussion_nb = discussion_nb


class Messaging:
    """
    Une messagerie (Messaging) est un objet qui peut envoyer des messages aux objets.
    Il a une liste de receveurs, et lorsque quelqu'un envoie un message, tous les receveurs reçoivent ce message.
    Si ce message leur est attribué, ils pourront l'utiliser, sinon, il sera ignoré.
    """
    def __init__(self):
        self.receivers = []

    def add_receiver(self, receiver):
        self.receivers.append(receiver)

    def remove_receiver(self, receiver):
        self.receivers.remove(receiver)

    def notify(self, message: Message):
        """ Send the message to every receiver """
        for receiver in self.receivers:
            receiver.notify(message)
