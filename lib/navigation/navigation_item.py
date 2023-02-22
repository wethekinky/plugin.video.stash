import json
from abc import ABC, abstractmethod
from typing import List, Tuple

import xbmc
import xbmcgui
import xbmcplugin

from lib import utils
from lib.stash_interface import StashInterface


class NavigationItem(ABC):
    handle: int

    def __init__(self, client: StashInterface, _type: str, label: str, browse_for: str):
        self._client = client
        self._type = _type
        self._browse_for = browse_for
        self._label = label

    def get_root_item(self) -> Tuple[xbmcgui.ListItem, str]:
        return xbmcgui.ListItem(label=self._label), utils.get_url(
            browse=self._type, browse_for=self._browse_for
        )

    def list_items(self):
        xbmcplugin.setPluginCategory(self.handle, self._label)
        xbmcplugin.setContent(self.handle, "videos")

        for item, url in self._create_items():
            xbmcplugin.addDirectoryItem(self.handle, url, item, True)

        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(self.handle)

    @abstractmethod
    def _create_items(self) -> List[Tuple[xbmcgui.ListItem, str]]:
        pass

    def _create_item(
        self, title: str, description: str = "", image_path: str = ""
    ) -> xbmcgui.ListItem:
        item = xbmcgui.ListItem(label=title)

        vinfo: xbmc.InfoTagVideo = item.getVideoInfoTag()
        vinfo.setMediaType("video")
        vinfo.setTitle(title)
        vinfo.setPlot(description)

        if image_path != "":
            image_path = self._client.add_api_key(image_path)
            item.setArt({"thumb": image_path, "fanart": image_path})

        return item

    def _create_url(self, title: str, criterion: dict, **kwargs) -> str:
        kwargs["criterion"] = json.dumps(criterion)
        kwargs["list"] = self._browse_for
        kwargs["title"] = title
        return utils.get_url(**kwargs)