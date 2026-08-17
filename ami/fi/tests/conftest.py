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
        "sub": "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060",
    }
