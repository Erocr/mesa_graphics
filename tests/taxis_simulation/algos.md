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

Voiture lors de la récéption de "passenger posX posY goalX goalY" pas sender :
    Si state == TRANSPORT :
        calcul chemin minimisant coût supplémentaire pour transporter cette personne
        si ce chemin est plus petit que longueur de path + epsilon et est plus petit que longueur de path_if_accepted:
            path_if_accepted = ce chemin
        
    
```
