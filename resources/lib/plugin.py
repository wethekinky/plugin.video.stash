import sys
from typing import Optional
from urllib.parse import parse_qsl

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from resources.lib import utils
from resources.lib.listing import Listing, SceneListing, create_listing
from resources.lib.navigation import NavigationItem
from resources.lib.stash_interface import StashInterface

utils.BASE_URL = sys.argv[0]
_HANDLE = int(sys.argv[1])
NavigationItem.handle = _HANDLE
Listing.handle = _HANDLE
_ADDON = xbmcaddon.Addon()
API_KEY: str = ''
CLIENT: Optional[StashInterface] = None


def run():
    global API_KEY
    global CLIENT
    API_KEY = _ADDON.getSetting('api_key')
    CLIENT = StashInterface(_ADDON.getSetting('base_url'), API_KEY)
    router(sys.argv[2][1:])


def browse_root():
    xbmcplugin.setPluginCategory(_HANDLE, 'Stash')
    xbmcplugin.setContent(_HANDLE, 'videos')

    listing = SceneListing(CLIENT)
    for (item, url) in listing.get_filters():
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    (item, url) = listing.get_root_item(utils.local.get_localized(30002))
    xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    for nav_item in listing.get_navigation():
        (item, url) = nav_item.get_root_item()
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    item = xbmcgui.ListItem(label=utils.local.get_localized(30010))
    url = utils.get_url(browse='scene_markers')
    xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(_HANDLE)


def browse(params):
    xbmcplugin.setPluginCategory(_HANDLE, 'Stash')
    xbmcplugin.setContent(_HANDLE, 'videos')

    listing = create_listing(params['browse'], CLIENT)
    for (item, url) in listing.get_filters():
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    (item, url) = listing.get_root_item(utils.local.get_localized(30002))
    xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    for navItem in listing.get_navigation():
        (item, url) = navItem.get_root_item()
        xbmcplugin.addDirectoryItem(_HANDLE, url, item, True)

    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(_HANDLE)


def list_items(params: dict):
    listing = create_listing(params['list'], CLIENT)
    listing.list_items(params)


def browse_for(params: dict):
    listing = create_listing(params['browse_for'], CLIENT)
    navigation = listing.get_navigation_item(params)
    navigation.list_items()


def play(params: dict):
    scene = CLIENT.find_scene(params['play'])
    item = xbmcgui.ListItem(path=scene['paths']['stream'])
    xbmcplugin.setResolvedUrl(_HANDLE, True, listitem=item)


def increment_o(params: dict):
    if 'scene' in params:
        o_count = CLIENT.scene_increment_o(params['scene'])
        xbmc.executebuiltin('Notification(Stash, {} {})'.format(
            utils.local.get_localized(30009), o_count))


def router(param_string: str):
    params = dict(parse_qsl(param_string, keep_blank_values=True))

    if params:
        if 'browse_for' in params:
            browse_for(params)
        elif 'browse' in params:
            browse(params)
        elif 'list' in params:
            list_items(params)
        elif 'play' in params:
            play(params)
        elif 'increment_o' in params:
            increment_o(params)
    else:
        browse_root()
