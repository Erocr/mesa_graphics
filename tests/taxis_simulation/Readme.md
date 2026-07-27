# Simulation de traffic avec mesa

## Sommaire


## 1. Utilisation

### Installation

Commencez par suivre le tutoriel d'installation de mesa_graphics :

Installez les bibliothèques nécessaires.
```bash
pip install mesa networkx altair matplotlib solara pygame
```
Enfin, installez mesa_graphics
```bash
cd projectFolder
git clone --filter=blob:none --sparse https://github.com/Erocr/mesa_graphics.git
cd mesa_graphics
git sparse-checkout set mesa_graphics
```

Pour lancer le projet, il suffit de lancer Viz.py. C'est le fichier qui s'occupe de l'interface graphique.

### Différents éléments

Dans la partie droite de l'écran, on a les composants.
Tout en haut, on a la grille avec le terrain et les voitures.
Ensuite, on a des graphiques représentant la vitesse moyenne et le nombre de voitures statiques.

À gauche, on a les paramètres pour modifier ce qui se passe à l'écran.

Play interval et render interval permettent de changer la vitesse d'exécution, et le nombre d'updates du modèle par frame.

**number_of_cars** est le nombre de voitures (ne doit pas dépasser le nombre de cases libres)  
**max_speed** est la vitesse maximale des voitures  
**length_of_the_route** est la longueur de la route. Si elle dépasse celle définie par l'utilisateur, la route va être 
collée plusieurs fois jusqu'à avoir la bonne taille  
**map** est le nom du fichier json qui contient les informations de la grille

### Carte personnalisée

Les cartes sont définies dans des fichiers json.

Il y a toujours 2 éléments : tile_types et grid. On commence par y définir les types de cases, et enfin, on les place dans la grille.

```json
{
  "tile_types" : ...,
  "grid" : ...
}
```

Dans tile_types, on va associer à des identifiants un type. Et on remplit la grille de ces identifiants.
Par exemple :
```json
{
  "tile_types": {
    "0": {
      "road": false
    },
    "1": {
      "road": true
    }
  },

  "grid": [[0, 0, 0],
           [1, 1, 1],
           [0, 0, 0]]
}
```

### Paramètres du type de tuiles

Voici une liste des différents paramètres pour la définition de types de tuiles :

#### road
A true la voiture peut y aller dessus, à false la voiture ne peut pas

#### directions
Les directions acceptées par la case. La voiture doit arriver sur cette case avec une de ces directions.

#### traffic light

Les feux de circulation. Ils sont définis comme des dictionnaires. Les paramètres sont
- **time** : le nombre de steps avant de changer d'état
- **states** : les directions autorisées pour chaque état

Par exemple
```json
{
  "road": true,
  "traffic light": {
    "time": 10,
    "states": [["right"], ["down"]]
  }
}
```

## 2. Explication du fonctionnement

### Modèle (Model)

Le modèle contient le monde.

Il a les choses classiques de mesa (DataCollector / Grid).
En plus de cela le modèle va stocker :
- **free_pos** : les tuiles de route (où les voitures peuvent aller)
- **_accepted_directions** : Un dictionnaire qui associe aux tuiles l'ensemble des directions acceptées pour la tuiles.
Une voiture ne peut arriver sur cette case qu'avec une de ces directions.

### Voiture (Car)

La voiture est un agent qui se trouve sur la grille.

La voiture va avoir une vitesse et une direction. Elle aura un compteur qui va de 0 à max_speed, où max_speed est la 
vitesse maximale que peut atteindre la voiture.

Lorsque le compteur atteint max_speed, alors la voiture avance, et va dans la prochaine case.
Pour avancer, la voiture a différentes possibilités. Si elle le peut, elle va tout droit. Si la case de devant est 
bloquée, ou en sens interdit, elle va tourner.

L'accélération de la voiture dépend des obstacles aux alentours. Si elle peut aller tout droit, alors elle va accélérer 
au maximum. Si elle peut tourner, et qu'elle ne peut pas aller tout droit, elle va accélérer jusqu'à un seuil. Enfin, si
elle est bloquée, elle va freiner brusquement, et arriver à une vitesse de 0.

L'implémentation est faite via des fonctions **perception** / **délibération** / **action**.

- **Perception** (perceive) : Il va regarder les cases devant à gauche et à droite de la voiture, et va stocker toutes les 
informations utiles de ces cases (et ses directions acceptées)
- **Délibération** (deliberate) : Choisit l'action que devra exécuter la voiture. L'action est un vecteur décrivant vers où est-ce 
qu'elle avance.
- **Action** (do) : Exécute l'action choisie durant la délibération. Elle commence par changer la vitesse suivant si elle 
va tout droit, tourne, ou pile. Ensuite, elle change le compteur de position. Si le compteur de position dépasse la vitesse maximale,
la voiture avance en suivant le vecteur choisit dans la délibération.

### Feu de circulation (TrafficLight)

Le feu de circulation est un agent sur la grille, comme la voiture. 
Le feu de circulation a un timer. Lorsque ce timer arrive au max (state_duration), il change son compteur d'état, et 
change les directions acceptées par la case sur laquelle il est. 