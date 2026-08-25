import pytest


@pytest.fixture
def decoded_user_data():
    return {
        "birthcountry": "99100",
        "birthdate": "1962-08-24",
        "birthplace": "75107",
        "family_name": "DUBOIS",
        "gender": "female",
        "given_name": "Angela Claire Louise",
        "sub": "01d6f14bd06de19c43c2984da5fb1a6941ac7d964f2a7c191d696e4a76aaf986",
    }
