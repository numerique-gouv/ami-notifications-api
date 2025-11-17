import urllib.parse


def url_contains_param(param_name: str, param_value: str, url: str) -> bool:
    url_encoded_value = urllib.parse.quote_plus(param_value)
    return f"{param_name}={url_encoded_value}" in url
