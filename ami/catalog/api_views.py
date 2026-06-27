from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from ami.authentication.decorators import ami_login_required
from ami.utils.schemas import DurationExpiration, TimeUnit

from .data.internal import get_internal_catalog
from .schemas import Catalog, CatalogItemsStatus
from .serializers import CatalogSerializer

CATALOG_EXPIRATION_RULES = {
    "internal": DurationExpiration(amount=5, unit=TimeUnit.MINUTES),
}


@api_view(["GET"])
@ami_login_required
def get_catalog(request: Request) -> Response[Catalog]:
    catalog = Catalog()

    catalogs_mapping = {
        "internal": get_internal_catalog,
    }

    for catalog_name in catalogs_mapping:
        result = catalogs_mapping[catalog_name]()
        if result.status == CatalogItemsStatus.SUCCESS:
            result.set_expires_at(CATALOG_EXPIRATION_RULES[catalog_name])
        catalog.__dict__[catalog_name] = result
    return Response(CatalogSerializer(catalog).data)
