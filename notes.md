# Notes

Le but de ce fichier est d'écrire des notes, mes pensées sur ce problème. Ce fichier sera aussi utile pour le rapport 
final.


## Architecture

On voudrait que la syntaxe soit identique à celle de Solara (ou le plus possible). Afin de pouvoir facilement 
interchanger entre l'un et l'autre.

Cela est une contrainte très forte, et qui nous indique déjà à quoi va ressembler l'architecture. Il faudra que les 
entêtes soient les mêmes que celles dans `mesa.visualization`. On devra donc réécrire à peu près toutes les 
classes/fonctions décrites [ici](https://mesa.readthedocs.io/stable/apis/visualization.html).

Ce qui va changer par contre, sera comment l'afficher. Dans solara, on entrait une ligne de commande `solara run 
app.py`. Cette méthode complexifie beaucoup l'architecture et l'utilisation pour peu de bénéfices. La meilleure 
méthode semble donc d'ajouter une classe View qui une fois créée, lance l'interface graphique. L'utilisateur
devra donc remplacer `page = SolaraViz(...)` par `view = View(...)`

On remarque qu'on pourrait aussi appeler la classe SolarViz, ainsi l'utilisateur n'aurait strictement aucune 
modification à faire autre que changer les imports. 

Cette architecture est très satisfaisante aussi, car elle respecte le motif d'architectures MVC (Model-View-Controller).
Ici, le Model serait le modèle de mesa, le View serait notre classe View, et le Controller serait une autre classe qu'on
créerait en même temps que le View.

## Comment faire mieux que l'interface de Solara

Solara est tourné sur un serveur. Mais en plus de cela, plusieurs points semblent peu ergonomiques.

### Les problèmes / améliorations potentielles

Voici une liste de points peu ergonomiques :
- Si on change les paramètres du modèle pendant l'exécution, tout plante (un message d'erreur moche apparaît, n'arrive
pas à chaque fois)
- Si on appuie beaucoup de fois sur le bouton step, il ne va plus prendre en compte les autres inputs **(ce problème 
n'est plus lorsque multithread est activé)**
- Il n'y a pas de boutons "retour en arrière", alors que le datacollector rendrait cette modification assez simple
- Cela semble intéressant d'afficher les informations des agents lorsqu'on passe la souris dessus
- Les agents sont affichés superposés s'il y en a plusieurs sur la même case
- La grille est potentiellement trop petite
- Ce serait intéressant de pouvoir changer certains attributs pendant l'exécution, sans avoir à reset

