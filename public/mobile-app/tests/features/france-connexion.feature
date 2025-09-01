# language: fr

Fonctionnalité: France Connect

    Règle: (@TODO - orienté partenaires et permettant de générer la documentation publique)

    # Objectifs (dans quel ordre ?) :
    #     - Tech: Se connecter sur AMI via France Connect
    #     - UX: Identifier les rupture de parcours quand on passe d'AMI à un fournisseur de service partenaire
    #     - Orga: Apprendre à travailler ensemble

    # Contexte : on imagine, en plus d'AMI, un fournisseur de service (FS) fictif de prise de rendez-vous "MesRendezVous". Ce FS permet à un usager de voir le détail d'un rendez-vous avec la possibilité de le supprimer, et d'autre part à un agent d'envoyer au nom de "MesRendezVous" une notification, via une interface propre à eux qui appellera AMI.

    Scénario: enregistrement d'un usager au service de notification d'AMI via France Connect
        Etant donné que l'usager est sur la home page non connectée de l'application AMI
        Quand l'usager se connecte sur AMI via France Connect en tant que "Camille" et suit le process de france connexion 
        Alors l'usager devrait arriver sur la home page connectée de l'application AMI
        Et l'usager "Camille" devrait être notifiable

        # Remarque : une première itération peut ignorer tout le process FC pour juste renvoyer des données en dur / aléatoire.

    Scénario: déconnexion d'un usager
        Etant donné que un admin se connecte au back-office de MesRendezVous
        Et que l'admin envoie à l'usager "Camille" un message Un rendez-vous "xxx" a été créé
        Etant donné que l'usager est sur la home page non connectée de l'application AMI
        Et que l'usager se connecte sur AMI via France Connect en tant que "Camille" et suit le process de france connexion
        Quand l'usager accède au détail du rendez-vous "xxx" sur AMI
        Alors la page de détail du rendez-vous "xxx" devrait s'afficher
        Quand l'usager se déconnecte
        Alors l'usage devrait être sur la home page non connectée de l'application AMI
        Quand l'usager accède au détail du rendez-vous "xxx" sur AMI
        Alors une page accès interdit devrait s'afficher


    Scénario: notification sur AMI via le service MesRendezVous
        Etant donné que l'usager "Camille" est "notifiable"
        Et que l'usager "Camille" autorise les notifications venant d'AMI
        Et que un admin se connecte au back-office de MesRendezVous
        Quand l'admin envoie à l'usager "Camille" un message Un rendez-vous "xxx" a été créé
        Alors l'usager "Camille" devrait recevoir une notification avec un lien lui permettant de visiter le page du rendez-vous "xxx" sur AMI
        Et le rendez-vous "xxx" apparait dans l'encours de l'usager "Camille" sur AMI

        # Questions : comment MesRendezVous connait les usagers notifiables ? Est-ce le même ID partagé par tous les services, en l'occurence MesRendezVous et AMI ? Ici, on va utiliser le même bac-à-sable chez FranceConnect donc on ne pourra s'en assurer. (cf rem. https://github.com/numerique-gouv/ami-notifications-api/issues/68#issuecomment-3078592712)
        # - peut-on demander à France Connect la création d'un autre bac-à-sable pour valider cela ?
        # Que se passe-t-il si l'usager n'est pas encore notifiable ? Peut-on récupérer les rendez-vous existant ? cf Atelier TECH 6/05 https://miro.com/app/board/uXjVI5hoo5o=/ et Scénario 2 de https://miro.com/app/board/uXjVI_HCqng=/?moveToWidget=3458764630638239223&cot=14. Comment gérer les stocks / les incohérences ? Ou faut-il faire appel à une API en //. Ou n'avons nous que des notif et pas l'encours ?
        # Question : peut-on enregistrer le fait que l'usager a accepté les notifications ?

    Scénario: accès au détail du rendez-vous sur MesRendezVous via authentification France Connect
        Etant donné que aucun usager n'est authentifié sur l'application MesRendezVous
        Et que l'usager se connecte sur AMI via France Connect en tant que "Camille" et suit le process de france connexion
        Et que l'usager accède au détail du rendez-vous "xxx" sur AMI
        Alors la page de détail du rendez-vous "xxx" devrait s'afficher
        Quand l'usager demande l'annulation du rendez-vous "xxx" sur AMI
        Alors l'usager devrait arriver sur la page de connexion de MesRendezVous 
        # dans l'appli ou dans un onglet nouvellement ouvert du navigateur par défaut ?
        Quand l'usager se connecte sur MesRendezVous via France Connect en tant que "Camille" et suit le process de france connexion
        # diffère si > ou < à 30 min depuis la dernière france connexion 
        Alors l'usager devrait voir le détail du rendez-vous "xxx" sur MesRendezVous et pouvoir l'annuler
        Et l'usager devrait être connecté sur MesRendezVous en tant que "Camille"

    Scénario: alternative : accès au détail du rendez-vous sur MesRendezVous via authentification allégée
        Etant donné que aucun usager n'est authentifié sur l'application MesRendezVous
        Et que l'usager se connecte sur AMI via France Connect en tant que "Camille" et suit le process de france connexion
        Et que l'usager accède au détail du rendez-vous "xxx" sur AMI
        Quand l'usager demande l'annulation du rendez-vous "xxx" sur AMI
        Alors l'usager devrait voir le détail du rendez-vous "xxx" sur MesRendezVous et pouvoir l'annuler
        Et l'usager ne devrait pas être connecté sur MesRendezVous

        # et si MesRendezVous nous fait suffisement confiance, il pourrait même considérer que le lien venant d'AMI vaut pour authentification de niveau FranceConnect et alors l'usager devrait être connecté sur MesRendezVous en tant que "Camille"


    # Ce qui mène à ce brief UI:
    #     - la PWA AMI permet 1) d'activer les notifications sur son device 2) de se connecter via FranceConnect 3) d'accéder à toutes ses notifications 4) d'accéder à son encours de rendez-vous avec un bouton permettant d'annuler un rendez-vous allant vers le fournisseur de service partenaire
    #     - l'application fictive MesRendezVous permet de 1) se connecter via FranceConnect, 2) d'afficher le détail d'un rendez-vous avec un bouton permettant de l'annuler
    #     - l'application fictive d'admin MesRendezVous qui permet de notifier un usager de la création d'un rendez-vous
    
