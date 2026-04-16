"""
Mapper entre l'adresse retournée par l'API Particulier (CAF/quotient familial)
et le Core Location Vocabulary (W3C/ISA²).

Référence : https://semiceu.github.io/Core-Location-Vocabulary/
Namespace  : http://www.w3.org/ns/locn#

Correspondance des champs
─────────────────────────────────────────────────────────────────
API Particulier (CAF)        │ Core Location Vocabulary
─────────────────────────────────────────────────────────────────
numero_libelle_voie          │ locn:thoroughfare
                             │   → nom de la voie (rue, avenue…)
lieu_dit                     │ locn:locatorName
                             │   → lieu-dit ou complément d'adresse
code_postal_ville            │ locn:postCode + locn:postName
                             │   → "75001 Paris" → séparé au premier espace
pays                         │ locn:adminUnitL1
                             │   → pays (niveau administratif 1)
─────────────────────────────────────────────────────────────────

Le résultat suit la structure d'une locn:Address sérialisée en JSON-LD,
conformément aux recommandations du Core Location Vocabulary v2.1.0.
"""

from __future__ import annotations

LOCN_CONTEXT = {
    "locn": "http://www.w3.org/ns/locn#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}

LOCN_ADDRESS_TYPE = "locn:Address"


def _split_code_postal_ville(code_postal_ville: str) -> tuple[str, str]:
    """
    Extrait le code postal et le nom de la ville depuis la chaîne CAF.

    L'API Particulier retourne une chaîne de la forme "75001 PARIS".
    Le code postal est le premier token, le reste forme le nom de la commune.

    Exemples :
        "75001 PARIS"          → ("75001", "PARIS")
        "13001 MARSEILLE 01"   → ("13001", "MARSEILLE 01")
        "75001"                → ("75001", "")
        ""                     → ("", "")
    """
    if not code_postal_ville:
        return "", ""
    parts = code_postal_ville.strip().split(" ", 1)
    post_code = parts[0] if parts else ""
    post_name = parts[1].strip() if len(parts) > 1 else ""
    return post_code, post_name


def map_caf_adresse_to_core_location(adresse: dict[str, str]) -> dict:
    """
    Transforme un bloc `adresse` de l'API Particulier en une locn:Address
    conforme au Core Location Vocabulary (JSON-LD).

    Paramètres
    ----------
    adresse : dict
        Dictionnaire brut retourné dans data["data"]["adresse"] par l'API
        Particulier / CAF. Champs attendus (tous optionnels) :
            - numero_libelle_voie
            - lieu_dit
            - code_postal_ville
            - pays

    Retour
    ------
    dict
        Objet JSON-LD représentant une locn:Address. Les propriétés absentes
        ou vides sont omises du résultat.

    Exemple
    -------
    Entrée (API Particulier) :
        {
            "numero_libelle_voie": "12 RUE DE LA PAIX",
            "lieu_dit": "",
            "code_postal_ville": "75001 PARIS",
            "pays": "France"
        }

    Sortie (Core Location Vocabulary) :
        {
            "@context": { "locn": "http://www.w3.org/ns/locn#", ... },
            "@type": "locn:Address",
            "locn:thoroughfare": "12 RUE DE LA PAIX",
            "locn:postCode": "75001",
            "locn:postName": "PARIS",
            "locn:adminUnitL1": "France"
        }
    """
    post_code, post_name = _split_code_postal_ville(adresse.get("code_postal_ville", "") or "")

    # Construction de la locn:Address — on n'inclut que les champs non vides
    locn_address: dict[str, object] = {
        "@context": LOCN_CONTEXT,
        "@type": LOCN_ADDRESS_TYPE,
    }

    thoroughfare = (adresse.get("numero_libelle_voie") or "").strip()
    if thoroughfare:
        locn_address["locn:thoroughfare"] = thoroughfare

    locator_name = (adresse.get("lieu_dit") or "").strip()
    if locator_name:
        locn_address["locn:locatorName"] = locator_name

    if post_code:
        locn_address["locn:postCode"] = post_code

    if post_name:
        locn_address["locn:postName"] = post_name

    admin_unit = (adresse.get("pays") or "").strip()
    if admin_unit:
        locn_address["locn:adminUnitL1"] = admin_unit

    return locn_address
