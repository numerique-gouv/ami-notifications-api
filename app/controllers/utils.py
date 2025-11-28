from typing import Any

from litestar.enums import RequestEncodingType
from litestar.params import Body


def UrlEncodedBody(
    media_type: RequestEncodingType = RequestEncodingType.URL_ENCODED,
    **kwargs: Any,
) -> Any:
    """Custom Body parameter with form-urlencoded included as default media type.

    This ensures OpenApi web clients such as RapiDoc display individual form fields instead of a JSON textarea.
    """
    return Body(media_type=media_type, **kwargs)
