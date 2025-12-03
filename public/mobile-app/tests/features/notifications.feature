# language: fr

Fonctionnalité: Notifications

  Règle: (@TODO - orienté partenaires et permettant de générer la documentation publique)

    Scénario: notification sur AMI via le service MesRendezVous
      Etant donné que l'usager "Camille" est enregistrée
      Et que l'usager "Camille" autorise les notifications venant d'AMI
      Et que un admin se connecte au back-office de MesRendezVous
      Quand l'admin envoie à l'usager "Camille" un message de rappel de son rendez-vous "France Travail"
      Alors l'usager "Camille" devrait recevoir une notification avec un lien lui permettant de visiter le page du rendez-vous "France Travail" sur AMI
      Et le rendez-vous "France Travail" apparait dans l'encours de l'usager "Camille" sur AMI

        # Questions : comment MesRendezVous connait les usagers enregistrés ? Est-ce le même ID partagé par tous les services, en l'occurence MesRendezVous et AMI ? Ici, on va utiliser le même bac-à-sable chez FranceConnect donc on ne pourra s'en assurer. (cf rem. https://github.com/numerique-gouv/ami-notifications-api/issues/68#issuecomment-3078592712)
        # - peut-on demander à FranceConnect la création d'un autre bac-à-sable pour valider cela ?
        # Que se passe-t-il si l'usager n'est pas encore enregistré ? Peut-on récupérer les rendez-vous existant ? cf Atelier TECH 6/05 https://miro.com/app/board/uXjVI5hoo5o=/ et Scénario 2 de https://miro.com/app/board/uXjVI_HCqng=/?moveToWidget=3458764630638239223&cot=14. Comment gérer les stocks / les incohérences ? Ou faut-il faire appel à une API en //. Ou n'avons nous que des notif et pas l'encours ?
        # Question : peut-on enregistrer le fait que l'usager a accepté les notifications ?


