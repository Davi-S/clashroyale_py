from datetime import datetime

from box import Box, BoxList


class ClashRoyaleModel:
    def __init__(self, data: dict | list, is_from_cache: bool, timestamp: datetime, **kwargs) -> None:
        if isinstance(data, list):
            self._data = BoxList(data, **kwargs)
        else:
            self._data = Box(data, **kwargs)
        self._raw_data = data
        self._is_from_cache = is_from_cache
        self._timestamp = timestamp

    @property
    def data(self) -> Box | BoxList:
        return self._data

    @property
    def raw_data(self) -> dict | list:
        return self._raw_data

    @property
    def is_from_cache(self) -> bool:
        return self._is_from_cache

    @property
    def timestamp(self) -> datetime:
        return self._timestamp
