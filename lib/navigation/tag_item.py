from typing import List

from lib.stash_interface import StashInterface
from lib.utils import DirectoryItem, local

from .navigation_item import NavigationItem


class TagItem(NavigationItem):
    def __init__(self, client: StashInterface, browse_for: str, **kwargs):
        _type = kwargs["type"] if "type" in kwargs else "tags"
        label = kwargs["label"] if "label" in kwargs else local.get_localized(30004)
        NavigationItem.__init__(self, client, _type, label, browse_for)

        self._filter_name = kwargs["filter_name"] if "filter_name" in kwargs else _type

    def _create_items(self) -> List[DirectoryItem]:
        (_, tags) = self._client.find_tags(
            has_type="scenes" if self._type == "scene_tags" else self._browse_for
        )
        items: List[DirectoryItem] = []
        for tag in tags:
            criterion = {
                self._filter_name: {"modifier": "INCLUDES_ALL", "value": [tag["id"]]}
            }

            description = tag["description"] if tag["description"] is not None else ""
            parent_tags = ", ".join([t["name"] for t in tag["parents"]])
            if parent_tags:
                description += f"\nParents: {parent_tags}"
            child_tags = ", ".join([t["name"] for t in tag["children"]])
            if child_tags:
                description += f"\nChildren: {child_tags}"

            item = self._create_item(
                title=tag["name"],
                description=description,
                image_path=tag["image_path"] if tag.get("image_count", 0) > 0 else "",
            )
            url = self._create_url(tag["name"], criterion)
            items.append((url, item, True))

        return items
