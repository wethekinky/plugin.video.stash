import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union

import xbmc
import xbmcgui
import xbmcplugin

from lib import criterion_parser, utils
from lib.navigation import NavigationItem
from lib.stash_interface import StashInterface
from lib.utils import DirectoryItem, local


class Listing(ABC):
    """A Listing is a list of video files that can be played."""

    handle: int

    def __init__(self, client: StashInterface, _type: str, label: str, **kwargs):
        self._client = client
        self._type = _type
        self._label = label
        self._filter_type = kwargs["filter_type"] if "filter_type" in kwargs else None

    def list_items(self, params: dict):
        title = params["title"] if "title" in params else self._label

        criterion = json.loads(params["criterion"]) if "criterion" in params else {}
        sort_field: Optional[Union[str, int]] = (
            params["sort_field"] if "sort_field" in params else None
        )
        sort_dir: Optional[str] = params["sort_dir"] if "sort_dir" in params else "asc"

        xbmcplugin.setPluginCategory(self.handle, title)
        xbmcplugin.setContent(self.handle, "videos")

        for url, item, is_folder in self._create_items(
            criterion, sort_field, sort_dir, params
        ):
            xbmcplugin.addDirectoryItem(self.handle, url, item, is_folder)

        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(self.handle)

    def get_root_item(self, override_title: str = "") -> DirectoryItem:
        return (
            utils.get_url(list=self._type),
            xbmcgui.ListItem(
                label=override_title if override_title != "" else self._label
            ),
            True,
        )

    def get_filters(self) -> List[DirectoryItem]:
        if self._filter_type is None:
            return []

        items: List[DirectoryItem] = []
        default_filter = self._client.find_default_filter(self._filter_type)
        if default_filter is not None:
            items.append(
                self._create_item_from_filter(
                    default_filter, local.get_localized(30007)
                )
            )
        else:
            item = xbmcgui.ListItem(label=local.get_localized(30007))
            url = utils.get_url(list=self._type)
            items.append((url, item, True))

        saved_filters = self._client.find_saved_filters(self._filter_type)

        for saved_filter in saved_filters:
            items.append(self._create_item_from_filter(saved_filter))

        return items

    @abstractmethod
    def get_navigation(self) -> List[NavigationItem]:
        pass

    @abstractmethod
    def get_navigation_item(self, params: dict) -> Optional[NavigationItem]:
        pass

    @abstractmethod
    def _create_items(
        self,
        criterion: dict,
        sort_field: Optional[str],
        sort_dir: Optional[Union[str, int]],
        params: dict,
    ) -> List[DirectoryItem]:
        pass

    def _create_item(self, scene: dict, **kwargs) -> xbmcgui.ListItem:
        title = kwargs["title"] if "title" in kwargs else scene["title"]

        screenshot = (
            kwargs["screenshot"]
            if "screenshot" in kwargs
            else scene["paths"]["screenshot"]
        )

        # grab the first file from the list of files
        files: List[Dict] = scene.get("files", [{}])
        file: Dict = files[0]

        duration = int(file["duration"])
        if not title:
            title = file["basename"]

        item: xbmcgui.ListItem = xbmcgui.ListItem(label=title)

        vinfo: xbmc.InfoTagVideo = item.getVideoInfoTag()
        vinfo.setTitle(title)
        vinfo.setMediaType("video")
        vinfo.setPlot(scene["details"])
        vinfo.setCast(
            [
                xbmc.Actor(
                    name=performer["name"]
                    if not performer["disambiguation"]
                    else f"{performer['name']} ({performer['disambiguation']})",
                    thumbnail=self._client.add_api_key(performer["image_path"]),
                )
                for performer in scene["performers"]
            ]
        )

        if scene["studio"] is not None:
            vinfo.setStudios([scene["studio"]["name"]])
        if scene.get("rating100", None) is not None:
            vinfo.setUserRating(scene["rating100"])
        vinfo.setPremiered(scene["date"])
        vinfo.setTags([t["name"] for t in scene["tags"]])
        vinfo.setDateAdded(scene["created_at"])
        vinfo.setDuration(duration)

        vinfo.addVideoStream(
            xbmc.VideoStreamDetail(
                width=file["width"],
                height=file["height"],
                duration=duration,
                codec=file["video_codec"],
            )
        )
        vinfo.addAudioStream(xbmc.AudioStreamDetail(codec=file["audio_codec"]))

        screenshot = self._client.add_api_key(screenshot)
        item.setArt({"thumb": screenshot, "fanart": screenshot})

        item.setProperty("IsPlayable", "true")

        return item

    @staticmethod
    def _create_play_url(scene_id: int, **kwargs):
        kwargs["play"] = scene_id
        return utils.get_url(**kwargs)

    def _set_title(self, title: str):
        xbmcplugin.setPluginCategory(self.handle, title)

    def _create_item_from_filter(
        self, _filter: dict, override_title=None
    ) -> DirectoryItem:
        """Create an item from a filter. Filters are provided as JSON encoded strings."""

        title = override_title if override_title is not None else _filter["name"]
        item = xbmcgui.ListItem(label=title)
        filter_data = json.loads(_filter["filter"])
        criterion_json = json.dumps(criterion_parser.parse(filter_data["c"]))

        url = utils.get_url(
            list=self._type,
            title=title,
            criterion=criterion_json,
            sort_field=filter_data.get("sortby"),
            sort_dir=filter_data.get("sortdir"),
        )

        return url, item, True
