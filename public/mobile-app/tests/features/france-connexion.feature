Feature: France Connect

    Objectif:
        - Se connecter sur AMI via France Connect
        - Identifier les rupture de parcours quand on passe d'AMI à un fournisseur de service partenaire
        - Apprendre à travailler ensemble

    Context: Soient trois applicatifs
        - la WPA AMI permettant de s'enregistrer aux notifications
        - une application fictive MesRendezVous de prise de rendez-vous pour les usagers
        - une application d'administration de ce service fictif permettant de notifier un usager d'un rappel de rendez-vous

        Scenario: enregistrement d'un usager au service de notification via France Connect
            Etant donné que l'usager est sur la home page de l'application AMI, non connecté
            Quand l'usager se connecte sur AMI via France Connect en tant que "Marco" et suit le process de france connexion 
            Alors l'usager devrait arriver sur la page de l'application
            Et "Marco" devrait être enregistré dans les usagers notifiables avec son Id Pivot

            Questions : comment rajouter la notion d'application pour éviter d'avoir une relation 1:1 entre usager et app ?

            Remarques : une première itération peut sauter tout le process FC pour juste renvoyer des données en dur / aléatoire.

        Scenario: notification 
            Etant donné que un admin est connecté au back-office de MesRendezVous
            Et que "Marco" est enregistré dans les usagers notifiables
            Quand l'admin notifie l'utilisateur "Marco" avec le message Votre rendez-vous "xxx" a lieu demain
            Alors "Marco" devrait recevoir une notification avec un lien lui permettant à visiter le page du rendez-vous "xxx" sur AMI

            Questions : comment MesRendezVous connait les usagers notifiables ? Est-ce le même ID partagé par tous les services, en l'occurence MesRendezVous et AMI ? Ici, on va utiliser le même service fictif chez FranceConnect donc on ne pourra s'en assurer. (cf rem. https://github.com/numerique-gouv/ami-notifications-api/issues/68#issuecomment-3078592712)

        Scenario: accès au détail du rendez-vous via authentification France Connect
            Etant donné que personne n'est pas authentifié sur l'application MesRendezVous
            Et que L'usager visite le page de rendez-vous "xxx" sur AMI
            Quand il souhaite supprimer le rendez-vous "xxx" sur le service MesRendezVous
            Alors L'usager devrait arriver sur la page de connexion de MesRendezVous
            Quand l'usager se connecte sur MesRendezVous via France Connect en tant que "Marco" et suit le process de france connexion 
            Alors l'usager devrait voir le détail du rendez-vous "xxx" et pouvoir l'annuler
            Et l'usager devrait être connecté en tant que "Marco"

        Scenario: alternative : accès au détail du rendez-vous via authentification allégée
            Etant donné que personne n'est pas authentifié sur l'application MesRendezVous
            Et que L'usager visite le page de rendez-vous "xxx" sur AMI
            Quand il souhaite supprimer le rendez-vous "xxx" sur le service MesRendezVous
            Alors L'usager devrait arriver sur la page de vérification allégée d'identité
            Quand l'usager rentre "Marco" comme identification allégée 
            Alors l'usager devrait voir le détail du rendez-vous "xxx" et pouvoir l'annuler
            Et l'usager ne devrait pas être connecté


    Brief UI:
        - la WPA AMI permet 1) d'activer les notifications sur son device 2) de se connecter via FranceConnect 3) d'accéder à toutes ses notifications 4) d'accéder à ses rendez-vous avec un bouton permettant d'annuler un rendez-vous allant vers le fournisseur de service partenaire
        - l'application fictive MesRendezVous permet de 1) se connecter via FranceConnect, 1) d'accéder à un rendez-vous juste en mettant les trois premières lettres de son nom, 3) d'afficher le détail d'un rendez-vous avec un bouton permettant de l'annuler

Next : faire référence et si besoin confronter ça avec / s'intégrer aux scenarios UX présentés sur les deux miro (fonc et tech)
