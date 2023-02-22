from urllib.parse import urlencode

BASE_URL = ""


def get_url(**kwargs) -> str:
    return f"{BASE_URL}?{urlencode(kwargs)}"
