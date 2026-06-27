from ami.catalog.models import Procedure
from ami.catalog.schemas import CatalogItem, CatalogItems, CatalogItemsStatus


def get_internal_data() -> list[CatalogItem]:
    procedures = Procedure.objects.all().order_by("title")

    return [procedure.to_catalog_item() for procedure in procedures]


def get_internal_catalog() -> CatalogItems:
    catalog_items = CatalogItems()

    items = get_internal_data()

    catalog_items.items = items
    catalog_items.status = CatalogItemsStatus.SUCCESS

    return catalog_items
