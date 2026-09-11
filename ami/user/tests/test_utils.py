from ami.user.utils import build_fc_hash


def test_build_fc_hash() -> None:
    given_name = "Angela Claire Louise"
    family_name = "DUBOIS"
    birthdate = "1962-08-24"
    gender = "female"
    birthplace = "75107"
    birthcountry = "99100"
    response = build_fc_hash(
        given_name=given_name,
        family_name=family_name,
        birthdate=birthdate,
        gender=gender,
        birthplace=birthplace,
        birthcountry=birthcountry,
    )
    assert response == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"

    birthplace = ""
    response = build_fc_hash(
        given_name=given_name,
        family_name=family_name,
        birthdate=birthdate,
        gender=gender,
        birthplace=birthplace,
        birthcountry=birthcountry,
    )
    assert response == "7e74df2cbebae761eccedbc24b7fe589bb83137f7808a2930031f52c73d75efe"


def test_build_fc_hash_v2(settings) -> None:
    settings.FEATURE_FLAG_USE_FC_HASH_V2 = True
    given_name = "Angela Claire Louise"
    family_name = "DUBOIS"
    birthdate = "1962-08-24"
    gender = "female"
    birthplace = "75107"
    birthcountry = "99100"
    response = build_fc_hash(
        given_name=given_name,
        family_name=family_name,
        birthdate=birthdate,
        gender=gender,
        birthplace=birthplace,
        birthcountry=birthcountry,
    )
    assert response == "01d6f14bd06de19c43c2984da5fb1a6941ac7d964f2a7c191d696e4a76aaf986"

    birthplace = ""
    response = build_fc_hash(
        given_name=given_name,
        family_name=family_name,
        birthdate=birthdate,
        gender=gender,
        birthplace=birthplace,
        birthcountry=birthcountry,
    )
    assert response == "637dc281adf555ae8a8c35bf31f76306cf88938aea9a47d6dc96a73e7d6bd827"
