from typing import List, Tuple

import xbmcgui

from resources.lib.stash_interface import StashInterface
from resources.lib.utils import local

from .navigation_item import NavigationItem


class PerformerItem(NavigationItem):
    def __init__(self, client: StashInterface, browse_for: str):
        NavigationItem.__init__(
            self, client, 'performers', local.get_localized(30003), browse_for)

    def _create_items(self) -> List[Tuple[xbmcgui.ListItem, str]]:
        (_, performers) = self._client.find_performers()
        items = []
        for performer in performers:
            criterion = {
                'performers': {
                    'modifier': 'INCLUDES_ALL', 'value': [performer['id']]
                }
            }
            details = f'''Gender: {performer['gender']}
Scenes: {performer['scene_count']}
Aliases: {performer['aliases']}

{performer['details']}
'''
            item = self._create_item(
                performer['name'],
                details,
                performer['image_path']
            )
            url = self._create_url(performer['name'], criterion)
            items.append((item, url))

        return items
