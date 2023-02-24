from typing import List

from lib.stash_interface import StashInterface
from lib.utils import DirectoryItem, local

from .navigation_item import NavigationItem


class PerformerItem(NavigationItem):
    def __init__(self, client: StashInterface, browse_for: str):
        NavigationItem.__init__(
            self, client, "performers", local.get_localized(30003), browse_for
        )

    def _create_items(self) -> List[DirectoryItem]:
        (_, performers) = self._client.find_performers()
        items: List[DirectoryItem] = []
        for performer in performers:
            criterion = {
                "performers": {"modifier": "INCLUDES_ALL", "value": [performer["id"]]}
            }
            # if the performer has disambiguation information available, add it onto their name
            name = performer["name"]
            if performer["disambiguation"]:
                name = f"{name} ({performer['disambiguation']})"

            details = f"""Gender: {performer['gender']}
Aliases: {', '.join(performer['alias_list'])}

{performer['details']}
"""
            item = self._create_item(
                title=name,
                description=details,
                image_path=performer["image_path"]
                if performer.get("image_count", 0) > 0
                else "",
            )
            url = self._create_url(name, criterion)
            items.append((url, item, True))

        return items
