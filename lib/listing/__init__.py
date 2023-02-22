from lib.stash_interface import StashInterface

from .listing import Listing
from .scene_listing import SceneListing
from .scene_marker_listing import SceneMarkerListing


def create_listing(_type: str, client: StashInterface) -> Listing:
    if _type == "scene_markers":
        return SceneMarkerListing(client)
    return SceneListing(client)
