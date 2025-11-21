"""Setup any system wide httpx configuration here."""

import httpx

httpxClient = httpx.Client(timeout=60)
