import hashlib


def build_fc_hash(
    *,
    given_name: str,
    family_name: str,
    birthdate: str,
    gender: str,
    birthplace: str,
    birthcountry: str,
) -> str:
    recipient_fc_hash = hashlib.sha256()
    recipient_fc_hash.update(
        f"{given_name}{family_name}{birthdate}{gender}{birthplace}{birthcountry}".encode("utf-8")
    )
    return recipient_fc_hash.hexdigest()
