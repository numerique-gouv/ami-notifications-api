Feature: France Connect

    Objectif:
        - Se connecter sur AMI via France Connect
        - Identifier les rupture de parcours quand on passe d'AMI à un fournisseur de service partenaire
        - Apprendre à travailler ensemble

    Context: Soient trois applicatifs
        - la WPA AMI permettant de s'enregistrer aux notifications
        - une application fictive MesRendezVous de prise de rendez-vous pour les usagers
        - une application d'administration de ce service fictif permettant de notifier un usager de la création de rendez-vous

        Scenario: enregistrement d'un usager au service de notification via France Connect
            Etant donné que l'usager est sur la home page de l'application AMI, non connecté
            Quand l'usager se connecte sur AMI via France Connect en tant que "Camille" et suit le process de france connexion 
            Alors l'usager devrait arriver sur la page de l'application
            Et l'usager "Camille" devrait être enregistré dans les usagers notifiables avec son Id Pivot

            Questions : comment rajouter la notion d'application pour éviter d'avoir une relation 1:1 entre usager et app ?

            Remarques : 
            - une première itération peut sauter tout le process FC pour juste renvoyer des données en dur / aléatoire.
            - l'usager est notifiable même s'il n'a pas accepté les notifications

        Scenario: notification 
            Etant donné que l'usager "Camille" est enregistré dans AMI dans les usagers notifiables
            Et que l'usager "Camille" autorise les notifications dans AMI
            Et que un admin se connecte au back-office de MesRendezVous
            Quand l'admin notifie l'usager "Camille" avec le message Un rendez-vous "xxx" a été créé
            Alors l'usager "Camille" devrait recevoir une notification avec un lien lui permettant de visiter le page du rendez-vous "xxx" sur AMI

            Questions : comment MesRendezVous connait les usagers notifiables ? Est-ce le même ID partagé par tous les services, en l'occurence MesRendezVous et AMI ? Ici, on va utiliser le même service fictif chez FranceConnect donc on ne pourra s'en assurer. (cf rem. https://github.com/numerique-gouv/ami-notifications-api/issues/68#issuecomment-3078592712)
            - peut-on demander à France Connect la création d'un autre bac à sable por valider cela ?

        Scenario: accès au détail du rendez-vous sur MesRendezVous via authentification France Connect
            Etant donné que aucun usager n'est authentifié sur l'application MesRendezVous
            Et que l'usager se connecte sur AMI via France Connect en tant que "Camille" et suit le process de france connexion
            Et que l'usager visite le page de rendez-vous "xxx" sur AMI
            Quand l'usager demande la suppression du rendez-vous "xxx" sur AMI
            Alors l'usager devrait arriver sur la page de connexion de MesRendezVous
            Quand l'usager se connecte sur MesRendezVous via France Connect en tant que "Camille" et suit le process de france connexion 
            Alors l'usager devrait voir le détail du rendez-vous "xxx" sur MesRendezVous et pouvoir l'annuler
            Et l'usager devrait être connecté sur MesRendezVous en tant que "Camille"

        Scenario: alternative : accès au détail du rendez-vous sur MesRendezVous via authentification allégée
            Etant donné que aucun usager n'est authentifié sur l'application MesRendezVous
            Et que l'usager se connecte sur AMI via France Connect en tant que "Camille" et suit le process de france connexion
            Et que L'usager visite le page de rendez-vous "xxx" sur AMI
            Quand il souhaite supprimer le rendez-vous "xxx" sur le service MesRendezVous
            Alors L'usager devrait arriver sur la page de vérification allégée d'identité
            Quand l'usager rentre "Camille" comme identification allégée 
            Alors l'usager devrait voir le détail du rendez-vous "xxx" et pouvoir l'annuler
            Et l'usager ne devrait pas être connecté sur MesRendezVous


    Brief UI:
        - la WPA AMI permet 1) d'activer les notifications sur son device 2) de se connecter via FranceConnect 3) d'accéder à toutes ses notifications 4) d'accéder à ses rendez-vous avec un bouton permettant d'annuler un rendez-vous allant vers le fournisseur de service partenaire
        - l'application fictive MesRendezVous permet de 1) se connecter via FranceConnect, 2) d'accéder à un rendez-vous juste en mettant les trois premières lettres de son nom, 3) d'afficher le détail d'un rendez-vous avec un bouton permettant de l'annuler
        - l'application fictive d'admin MesRendezVous qui permet de notifier un usager de la création d'un rendez-vous

Next : faire référence et si besoin confronter ça avec / s'intégrer aux scenarios UX présentés sur les deux miro (fonc et tech)
