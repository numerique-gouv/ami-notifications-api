from rest_framework import serializers

from ami.notification.models import Notification


class NotificationReadSerializer(serializers.Serializer):
    read = serializers.BooleanField()


class NotificationResponseSerializer(serializers.Serializer):
    notification_id = serializers.UUIDField()
    notification_send_status = serializers.BooleanField()


class NotificationSerializer(serializers.ModelSerializer):
    # Remap the "user" field from the model to "user_id" in the serializer
    user_id = serializers.UUIDField(source="user.id")

    class Meta:
        fields = [
            "content_body",
            "content_icon",
            "content_title",
            "created_at",
            "id",
            "item_canal",
            "item_generic_status",
            "item_id",
            "item_milestone_end_date",
            "item_milestone_start_date",
            "item_status_label",
            "item_type",
            "url",
            "read",
            "user_id",
        ]
        model = Notification


class ScheduledNotificationCreateSerializer(serializers.Serializer):
    content_title = serializers.CharField(allow_blank=False)
    content_body = serializers.CharField(allow_blank=False)
    content_icon = serializers.CharField(allow_blank=False)
    reference = serializers.CharField(allow_blank=False)
    internal_url = serializers.CharField(allow_blank=False, default=None)
    scheduled_at = serializers.DateTimeField()


class ScheduledNotificationResponseSerializer(serializers.Serializer):
    scheduled_notification_id = serializers.UUIDField()


class ScheduledNotificationDeleteSerializer(serializers.Serializer):
    reference = serializers.CharField(allow_blank=False)


class PartnerNotificationCreateSerializer(serializers.Serializer):
    recipient_fc_hash = serializers.CharField(
        help_text="Hash de la concaténation des données pivot FC de l'usager destinataire, cf doc",
    )
    content_title = serializers.CharField(allow_blank=False, help_text="Titre de la notification")
    content_body = serializers.CharField(allow_blank=False, help_text="Contenu de la notification")
    content_icon = serializers.CharField(
        allow_blank=False,
        default=None,
        help_text="Nom technique de l'icône à associer à la notification dans l'application AMI, à choisir dans [les icones du DSFR](https://www.systeme-de-design.gouv.fr/version-courante/fr/fondamentaux/icone).",
    )
    item_type = serializers.CharField(
        allow_blank=False,
        help_text='Champ libre représentant le type de l\'objet associé à la notification, par exemple : "OTV" dans le cas des démarches "Opération Tranquillité Vacances"',
    )
    item_id = serializers.CharField(
        allow_blank=False,
        help_text="Identifiant dans le référentiel partenaire de l'objet associé à la notification",
    )
    item_status_label = serializers.CharField(
        allow_blank=False, help_text='objet associé à la notification, par exemple : "Brouillon"'
    )
    item_generic_status = serializers.ChoiceField(
        choices=["new", "wip", "closed"],
        help_text="Statut générique de l'objet associé à la notification pilotant des comportements spécifiques dans l'application AMI",
    )
    item_canal = serializers.CharField(
        allow_blank=False,
        default=None,
        help_text="Canal source de l'objet associé à la notification (AMI, PSL, etc.) pour la mesure d'impact",
    )
    item_milestone_start_date = serializers.DateTimeField(
        default=None,
        help_text="Date (au format ISO 8601) de début de la période correspondant à l'objet associé à la notification, ex : date de début de surveillance du logement dans le cadre d'une OTV",
    )
    item_milestone_end_date = serializers.DateTimeField(
        default=None,
        help_text="Date (au format ISO 8601) de fin de la période correspondant à l'objet associé à la notification, ex : date de fin de surveillance du logement dans le cadre d'une OTV",
    )
    item_external_url = serializers.CharField(
        allow_blank=False,
        default=None,
        help_text="Lien vers le portail du partenaire de l'objet associé à la notification",
    )
    send_date = serializers.DateTimeField(
        help_text="Date (au format ISO 8601) d'émission de la notification côté partenaire"
    )
    try_push = serializers.BooleanField(
        default=True,
        help_text="Indique si le système doit essayer de déclencher une Notification Push sur les terminaux de l'usager",
    )
