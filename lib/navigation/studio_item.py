from typing import List

from lib.stash_interface import StashInterface
from lib.utils import DirectoryItem, local

from .navigation_item import NavigationItem


class StudioItem(NavigationItem):
    def __init__(self, client: StashInterface, browse_for: str):
        NavigationItem.__init__(
            self, client, "studios", local.get_localized(30005), browse_for
        )

    def _create_items(self) -> List[DirectoryItem]:
        (_, studios) = self._client.find_studios()
        items: List[DirectoryItem] = []
        for studio in studios:
            criterion = {
                "studios": {
                    "modifier": "INCLUDES_ALL",
                    "value": [studio["id"]],
                    "depth": 0,
                }
            }
            item = self._create_item(
                studio["name"],
                studio["details"],
                studio["image_path"] if studio.get("image_count", 0) > 0 else "",
            )
            url = self._create_url(studio["name"], criterion)
            items.append((url, item, True))

        return items
