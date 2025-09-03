# language: fr

Fonctionnalité: France Connect

    Scénario: usager enregistré
        Etant donné que l'usager "Camille" est enregistrée
        Alors l'usager "Camille" devrait être enregistrée dans les usagers connus d'AMI avec son Id Pivot
        # Questions : comment rajouter la notion d'application pour éviter d'avoir une relation 1:1 entre usager et app ?

