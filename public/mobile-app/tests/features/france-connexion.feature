# language: fr

Fonctionnalité: France Connect

  Règle: (@TODO - orienté partenaires et permettant de générer la documentation publique)

    # Objectifs (dans quel ordre ?) :
    #     - Tech: Se connecter sur AMI via France Connect
    #     - UX: Identifier les rupture de parcours quand on passe d'AMI à un fournisseur de service partenaire
    #     - Orga: Apprendre à travailler ensemble

    # Contexte : on imagine, en plus d'AMI, un fournisseur de service (FS) fictif de prise de rendez-vous "MesRendezVous". Ce FS permet à un usager de voir le détail d'un rendez-vous avec la possibilité de le supprimer, et d'autre part à un agent d'envoyer au nom de "MesRendezVous" une notification, via une interface propre à eux qui appellera AMI.

    Scénario:
      Etant donné que l'usager est sur la home page non connectée de l'application AMI
      Quand l'usager clique sur le lien allant vers la démo
      Alors l'usager va vers la démo

    Scénario: enregistrement d'un usager au service de notification d'AMI via France Connect
      Etant donné que l'usager est sur la home page non connectée de l'application AMI
      Quand l'usager se connecte sur AMI via France Connect en tant que "Camille" et suit le process de france connexion
      Alors l'usager devrait arriver sur la home page connectée de l'application AMI
      Et l'usager "Camille" devrait être enregistrée

        # Remarque : une première itération peut ignorer tout le process FC pour juste renvoyer des données en dur / aléatoire.

    Scénario: déconnexion d'un usager
      Etant donné que l'usager est sur la home page non connectée de l'application AMI
      Et que l'usager se connecte sur AMI via France Connect en tant que "Camille" et suit le process de france connexion
      Quand l'usager accède au détail du rendez-vous "France Travail" sur AMI
      Alors la page de détail du rendez-vous "France Travail" devrait s'afficher
      Quand l'usager se déconnecte
      Alors l'usager devrait être sur la home page non connectée de l'application AMI
      #L'usager y accède par son historique, en cliquant back, ou en cliquant sur une notification concernant ce rdv par exemple
      Quand l'usager accède au détail du rendez-vous "France Travail" sur AMI
      Alors l'usager devrait être sur la home page non connectée de l'application AMI

    Scénario: redirection vers la page demandée après reconnexion
      Etant donné que l'usager est sur la home page non connectée de l'application AMI
      Quand l'usager accède au détail du rendez-vous "France Travail" sur AMI
      Alors l'usager devrait être sur la home page non connectée de l'application AMI
      Et un message devrait être affiché indiquant "pour accéder à cette page, merci de vous connecter"
      Quand l'usager se connecte sur AMI via France Connect en tant que "Camille" et suit le process de france connexion
      Alors la page de détail du rendez-vous "France Travail" devrait s'afficher

    # Ce qui mène à ce brief UI:
    #     - la PWA AMI permet 1) d'activer les notifications sur son device 2) de se connecter via FranceConnect 3) d'accéder à toutes ses notifications 4) d'accéder à son encours de rendez-vous avec un bouton permettant d'annuler un rendez-vous allant vers le fournisseur de service partenaire
    #     - l'application fictive MesRendezVous permet de 1) se connecter via FranceConnect, 2) d'afficher le détail d'un rendez-vous avec un bouton permettant de l'annuler
    #     - l'application fictive d'admin MesRendezVous qui permet de notifier un usager de la création d'un rendez-vous

