from typing import List, Optional

from lib.navigation import NavigationItem, PerformerItem, StudioItem, TagItem
from lib.stash_interface import StashInterface
from lib.utils import DirectoryItem, get_url, local

from .listing import Listing


class SceneListing(Listing):
    def __init__(self, client: StashInterface):
        Listing.__init__(
            self, client, "scenes", local.get_localized(30006), filter_type="SCENES"
        )

    def get_navigation(self) -> List[NavigationItem]:
        return [
            PerformerItem(self._client, "scenes"),
            TagItem(self._client, "scenes"),
            StudioItem(self._client, "scenes"),
        ]

    def get_navigation_item(self, params: dict) -> Optional[NavigationItem]:
        browse = params["browse"]
        if browse == "performers":
            return PerformerItem(self._client, "scenes")
        if browse == "tags":
            return TagItem(self._client, "scenes")
        if browse == "studios":
            return StudioItem(self._client, "scenes")

    def _create_items(
        self, criterion: dict, sort_field: str, sort_dir: str, params: dict
    ) -> List[DirectoryItem]:
        (_, scenes) = self._client.find_scenes(criterion, sort_field, sort_dir)
        items: List[DirectoryItem] = []
        for scene in scenes:
            item = self._create_item(scene)
            url = self._create_play_url(scene["id"])

            menu = []
            if len(scene["scene_markers"]) > 0:
                menu.append(
                    (
                        local.get_localized(30010),
                        f'ActivateWindow(videos, {get_url(list="scene_markers", scene=scene["id"])})',
                    )
                )
            menu.append(
                (
                    local.get_localized(30008),
                    f'RunPlugin({get_url(increment_o="", scene=scene["id"])})',
                )
            )
            item.addContextMenuItems(menu)

            items.append((url, item, False))

        return items
