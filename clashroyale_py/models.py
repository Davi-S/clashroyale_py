from datetime import datetime

from box import Box, BoxList


class ClashRoyaleModel:
    pass


class ClashRoyaleBoxModel(ClashRoyaleModel):
    def __init__(self, data: dict, is_from_cache: bool, timestamp: datetime, **kwargs) -> None:
        self._data = Box(data, **kwargs)
        self._raw_data = data
        self._is_from_cache = is_from_cache
        self._timestamp = timestamp

    @property
    def data(self) -> Box:
        return self._data

    @property
    def raw_data(self) -> dict:
        return self._raw_data

    @property
    def is_from_cache(self) -> bool:
        return self._is_from_cache

    @property
    def timestamp(self) -> datetime:
        return self._timestamp


class ClashRoyaleBoxListModel(ClashRoyaleModel):
    def __init__(self, data: list, is_from_cache: bool, timestamp: datetime, **kwargs) -> None:
        self._data = BoxList(data, **kwargs)
        self._raw_data = data
        self._is_from_cache = is_from_cache
        self._timestamp = timestamp

    @property
    def data(self) -> BoxList:
        return self._data

    @property
    def raw_data(self) -> list:
        return self._raw_data

    @property
    def is_from_cache(self) -> bool:
        return self._is_from_cache

    @property
    def timestamp(self) -> datetime:
        return self._timestamp
