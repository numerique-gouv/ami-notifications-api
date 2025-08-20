# language: fr

Fonctionnalité: France Connect

    Scénario: usager notifiable
        Etant donné que l'usager "Camille" est notifiable
        Alors l'usager "Camille" devrait être enregistré dans les usagers connus d'AMI avec son Id Pivot
        # Questions : comment rajouter la notion d'application pour éviter d'avoir une relation 1:1 entre usager et app ?
        # Remarques: L'usager est notifiable même s'il n'a pas accepté les notifications

