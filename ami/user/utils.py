import hashlib

from django.conf import settings


def build_fc_hash(
    *,
    given_name: str,
    family_name: str,
    birthdate: str,
    gender: str,
    birthplace: str,
    birthcountry: str,
) -> str:
    if settings.FEATURE_FLAG_USE_FC_HASH_V2:
        recipient_fc_hash = hashlib.sha256(
            f"{given_name};{family_name};{birthdate};{gender};{birthplace};{birthcountry}".encode()
        )
    else:
        recipient_fc_hash = hashlib.sha256(
            f"{given_name}{family_name}{birthdate}{gender}{birthplace}{birthcountry}".encode()
        )
    return recipient_fc_hash.hexdigest()
