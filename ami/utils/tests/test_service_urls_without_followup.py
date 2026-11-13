import pytest

from ami.partner.models import Partner
from ami.service.models import Service


@pytest.mark.django_db
def test_get_service_urls_without_followup(app, settings, partner_psl: Partner):
    response = app.get("/api-utils/service-urls-without-followup", status=200)
    assert response.json == {"service_urls_without_followup": []}

    Service.objects.create(
        kind=Service.Kind.SOS,
        partner=partner_psl,
        item_type="sos",
        with_followup_integration=False,
        url="http://service-sos",
    )
    Service.objects.create(
        kind=Service.Kind.STEPS,
        partner=partner_psl,
        item_type="steps",
        with_followup_integration=False,
        url="http://service-steps",
    )
    Service.objects.create(
        kind=Service.Kind.CATALOG,
        partner=partner_psl,
        item_type="catalog-True",
        with_followup_integration=True,
        url="http://service-catalog-True",
    )
    response = app.get("/api-utils/service-urls-without-followup", status=200)
    assert response.json == {"service_urls_without_followup": []}

    Service.objects.create(
        kind=Service.Kind.CATALOG,
        partner=partner_psl,
        item_type="catalog-False-1",
        with_followup_integration=False,
        url="http://service-catalog-False-1",
    )
    Service.objects.create(
        kind=Service.Kind.CATALOG,
        partner=partner_psl,
        item_type="catalog-False-2",
        with_followup_integration=False,
        url="http://service-catalog-False-2",
    )
    response = app.get("/api-utils/service-urls-without-followup", status=200)
    assert response.json == {
        "service_urls_without_followup": [
            "http://service-catalog-False-1",
            "http://service-catalog-False-2",
        ]
    }
