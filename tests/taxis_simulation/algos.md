## Présentation des algorithmes

### Algo de base

C'est l'algorithme de base, tous les autres algorithmes ajoutent des éléments à cet algorithme.
Pour l'écriture des algorithmes, je passe certains détails. Je vous prie d'aller voir le code pour plus de détails.

```
Vatiables internes de Passager :
    pos : Vecteur, sa position 
    goal : Vecteur, la position vers laquelle il veut aller
    transport : Voiture, la voiture qui le transporte
    best_car : Voiture, la voiture qui lui a fait la meilleur proposition jusque là
    best_dist : entier, la plus courte distance qu'il a reçu jusque là

Passager lors de l'apparition :
    Envoi de "passenger posX posY goalX goalY" à toutes les voitures
    
Passager lorsqu'il se fait transporter par une voiture :
    Envoi de "direction goalX goalY" à transport
    
Passager lors de la réception de "distance dist" envoyée par sender :
    si dist < best_dist :
        best_dist = dist
        best_car = sender
        
Passager après time_before_accept tours :
    Envoi de "ok" à best_car
    
    

Variables internes de Voiture :
    state : enum[IDLE, SENT_PROPOSITION, PROPOSITION_ACCEPTED, TRANSPORT], l'état courant de la voiture
    transport : Passager, la personne qu'il transporte
    sent_proposition : Passager, la personne à qui il a envoyé une proposition
    path : Chemin, un chemin stocké
    follow_path : bool, si la voiture suit le chemin
    
Voiture lors de la réception de "passenger posX posY goalX goalY" par sender : 
    Si state est à IDLE :
        calcul du chemin dans path
        envoi de "distance length(path)" à sender
        state = SENT_PROPOSITION
        sent_proposition = sender
        
Voiture lors de la récéption de "ok" par sender :
    Si state est à SENT_PROPOSITION :
        follow_path = True
        state = PROPOSITION_ACCEPTED
        
Voiture lorsque sa position est celle de sent_proposition :
    Si state est à PROPOSITION_ACCEPTED :
        state = TRANSPORT
        transport = sent_proposition
        calcul le chemin vers goal dans path
        follow_path = True
        
Voiture lorsque transport arrive à destination :
    state = IDLE
    follow_path = False
    
```

### Transport multiple : tolerance limitée

Cet algorithme part de la base de l'algorithme d'au-dessus. On va noter ici les différences avec celui d'au-dessus.


```
Variables internes : 
    transport : list[Voiture], à présent il peut transporter plusieurs voitures
    path_if_accepted : Chemin, 
    positions : list[Vecteur], les position par lesquelles il passe
    epsilon : flottant, limite de tolérance

Voiture lors de la récéption de "passenger posX posY goalX goalY" par sender :
    Si state == TRANSPORT :
        calcul chemin minimisant coût supplémentaire pour transporter cette personne  # explication plus précise plus bas
        si longueur du detour < epsilon:
            path_if_accepted = ce chemin
            envoi de "distance longueur_du_détour" à sender
            
Voiture lors de la récption de "ok" de sender :
    Si state == TRANSPORT :
        path = path_if_accepted
    
    exécute le code de la voiture de base ...
        
  
     
```

Voici une petite explication de comment calculer le chemin minimisant le coût supplémentaire.
Dans le cas présenté ci-dessus, la voiture a déjà pris un passager. 
Ainsi, elle a trois possibilités :
- Elle dépose le premier passager, puis va prendre le deuxième passager, enfin, il dépose le deuxième passager.
- Elle va prendre le deuxième passager, dépose le premier passager, et enfin dépose le deuxième passager
- Elle va prendre le deuxième passager, dépose le deuxième passager, et enfin dépose le premier passager

La première possibilité revient à ne pas utiliser la deuxième place. On l'ignore.

Le chemin dans le deuxième cas est :
- De la voiture au deuxième passager
- Du deuxième passager au point de dépôt du premier passager
- Du point de dépôt du premier passager au point de dépôt du deuxième passager

Le chemin dans le troisième cas :
- De la voiture au deuxième passager
- Du deuxième passager au point de dépôt du deuxième passager
- Du point de dépôt du deuxième passager au point de dépôt du premier passager

On peut alors choisir le chemin le plus court.

Enfin, on doit calculer le détour.
Pour cela, on calcule la différence entre la taille de ce chemin, et la taille du chemin minimal.
Le chemin minimal est le chemin que veulent parcourir les passagers. 
C'est-à-dire de la voiture au point de dépôt 1 plus du deuxième passager au point de dépôt 2

Si ce détour est inférieure à la tolérance, on le prend, sinon on l'oublie.



## Benchmarks et résultats

On lance les différents algos avec les mêmes paramètres et les mêmes seed, et on regarde combien de temps prend l'algo 
pour ramener tous les passagers.

Les scores sont un tout petit peu meilleurs en moyenne avec le deuxième algo. 
L'amélioration est très moindre, d'environ 5%.

Cela dit, il y a différents bugs dans l'implémentation, et l'implémentation n'est pas terminée. 
Ainsi, ce chiffre n'est pas réellement représentatif.
On voit entre autre que le deuxième algorithme semble être moins performant lorsqu'il y a plusieurs voitures. 
Cela peut s'expliquer par le fait que le système pour éviter les autres voitures n'a pas complètement été codé dans la 
deuxième version
