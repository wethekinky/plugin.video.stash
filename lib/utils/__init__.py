from typing import Tuple
from urllib.parse import urlencode

import xbmcgui

BASE_URL = ""

DirectoryItem = Tuple[str, xbmcgui.ListItem, bool]


def get_url(**kwargs) -> str:
    return f"{BASE_URL}?{urlencode(kwargs)}"
