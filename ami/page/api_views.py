from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, schema
from rest_framework.request import Request
from rest_framework.response import Response

from ami.authentication.decorators import ami_login_required
from ami.page.models import Page


@api_view(["GET"])
@ami_login_required
@schema(None)
def get_page(
    request: Request,
    page_slug: str,
) -> Response[Page]:
    page = get_object_or_404(Page, slug=page_slug)
    serialization = {
        "slug": page.slug,
        "title": page.title,
        "sections": [
            {
                "slug": x.slug,
                "title": x.title,
                "text": x.text,
            }
            for x in page.section_set.all()  # type: ignore[reportAttributeAccessIssue]
        ],
    }
    return Response(serialization)
