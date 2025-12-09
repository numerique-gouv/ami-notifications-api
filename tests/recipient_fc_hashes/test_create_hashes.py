import csv
from pathlib import Path

from app.utils import build_fc_hash


async def test_hash_from_csv() -> None:
    results = []

    BASE_DIR = Path(__file__).parent

    test_csv_path = BASE_DIR / "test.csv"

    with test_csv_path.open(mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=",")
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                given_name = row["prenoms"]
                family_name = row["nomDeNaissance"]
                birthdate = row["dateDeNaissance"]
                gender = row["genre"]
                birthplace = row["codePostalLieuDeNaissance"]
                birthcountry = row["codePaysDeNaissance"]
                response = build_fc_hash(
                    given_name=given_name,
                    family_name=family_name,
                    birthdate=birthdate,
                    gender=gender,
                    birthplace=birthplace,
                    birthcountry=birthcountry,
                )

                results.append(  # type: ignore[reportUnknownMemberType]
                    {
                        "id": row["id"],
                        "identifiant": row["identifiant"],
                        "prenoms": row["prenoms"],
                        "nomDeNaissance": row["nomDeNaissance"],
                        "dateDeNaissance": row["dateDeNaissance"],
                        "genre": row["genre"],
                        "codePostalLieuDeNaissance": row["codePostalLieuDeNaissance"],
                        "codePaysDeNaissance": row["codePaysDeNaissance"],
                        "hash": response,
                    }
                )

    test_results_csv_path = BASE_DIR / "test_results.csv"

    with test_results_csv_path.open(mode="w") as csv_file:
        fieldnames = [
            "id",
            "identifiant",
            "prenoms",
            "nomDeNaissance",
            "dateDeNaissance",
            "genre",
            "codePostalLieuDeNaissance",
            "codePaysDeNaissance",
            "hash",
        ]
        writer = csv.DictWriter(csv_file, delimiter=",", fieldnames=fieldnames)
        writer.writeheader()

        for row in results:  # type: ignore[reportUnknownVariableType]
            writer.writerow(
                {
                    "id": row["id"],
                    "identifiant": row["identifiant"],
                    "prenoms": row["prenoms"],
                    "nomDeNaissance": row["nomDeNaissance"],
                    "dateDeNaissance": row["dateDeNaissance"],
                    "genre": row["genre"],
                    "codePostalLieuDeNaissance": row["codePostalLieuDeNaissance"],
                    "codePaysDeNaissance": row["codePaysDeNaissance"],
                    "hash": row["hash"],
                }
            )
