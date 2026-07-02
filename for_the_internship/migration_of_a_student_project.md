## Installation du projet étudiant

- clone le repository.
- J'utilise pycharm, donc je n'ai pas besoin de faire de venv, etc, donc je saute.
- Je lance `pip install mesa==3.1.4 solara matplotlib pandas`. Attention : ce n'est pas la bonne version pour 
MesaGraphics !! Cela dit, il est intéressant de tester pour voir ce que MesaGraphics fait dans cette version.
- Je lance `pip install -r requirements.txt` pour être sûr que tout soit installé
- Je lance `solara run server.py`, tout marche, parfait.

## Installation de MesaGraphics

- Je clone le repository (dans le dossier Self-Organization-of-Robots-in-a-Hostile-Environnement): 
`git clone "https://github.com/Erocr/mesa_graphics.git"` 
- J'installe les requirements : `pip install -r .\mesa_graphics\requirements.txt`

## Migration Solara -> MesaGraphics

- Je copie colle le fichier sever.py, en le renommant dans mon exemple 'pygame_viz.py'
- Je change les imports :
```python
# Before
# from mesa.visualization import SolaraViz, make_plot_component
# try:
#     from mesa.visualization import make_space_component
# except ImportError:
#     from mesa.visualization.components.matplotlib_components import make_space_component

# After
from mesa_graphics import MesaGraphics, make_plot_component, make_space_component 
```
  - J'enlève l'import à Solara, ça me permet de savoir où sont tous les endroits où ils l'utilisent
  - On trouve un custom component :
````python
def make_legend(_model):
    return solara.Markdown("""
### Robots
| Symbole | Type | Zone |
|---------|------|------|
| ▲ Vert   | Collecte vert → jaune     | z1       |
| ■ Jaune  | Collecte jaune → rouge    | z1 + z2  |
| ◆ Rouge  | Transporte rouge → dépôt  | z1+z2+z3 |

### Déchets & Objets
| Symbole | Signification |
|---------|---------------|
| ● Vert   | Déchet vert  |
| ● Jaune  | Déchet jaune |
| ● Rouge  | Déchet rouge |
| ★ Bleu   | Zone de dépôt|
| ■ Noir   | Mur          |
""")
````
Il utilise directement une fonction de Solara, sans passer par mesa. On ne peut pas faire la migration automatiquement.
On est obligés de le transformer en format pygame. Je vais proposer une version avec pygame plus tard, mais pour 
l'instant, on l'enlèvera. (On supprime la fonction, et l'utilisation dans l'appel à SolaraViz)
- On remplace SolaraViz par MesaGraphics
- Mini-changement temporaire : Je n'ai pas encore implémenté les Select, donc je le remplace par un booléen. Dans le 
futur cette modification ne sera pas à faire.
- J'exécute pygame_viz.py : ça marche !!!! mesa_graphics marche donc aussi pour mesa 3.1.4, pas besoin de migrations
