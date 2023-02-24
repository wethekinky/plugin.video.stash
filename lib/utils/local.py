import xbmcaddon

_ADDON = xbmcaddon.Addon()


def get_localized(_id: int) -> str:
    return _ADDON.getLocalizedString(_id)
