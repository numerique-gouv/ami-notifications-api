"""Setup any system wide httpx configuration here."""

import httpx as do_not_use_httpx

httpx = do_not_use_httpx.Client(timeout=60)
