from rest_framework.exceptions import APIException


class MissingAuthHeader(APIException):
    status_code = 403
    default_detail = "Header d'authentification manquant"
    default_code = "missing-auth-header"


class WrongFormatAuthHeader(APIException):
    status_code = 403
    default_detail = "Header d'authentification mal formé"
    default_code = "wrong-format-auth-header"


class FISessionExpired(APIException):
    status_code = 403
    default_detail = "Session de connexion à AMI-FI expirée"
    default_code = "fi-session-expired"


class FISessionNotFound(APIException):
    status_code = 403
    default_detail = "Session de connexion à AMI-FI non trouvée"
    default_code = "fi-session-not-found"
