from datetime import datetime

from box import Box, BoxList


class ClashRoyaleModel:
    # TODO: Use generic types for return values. Specially for the "data" and "raw_data"
    def __init__(self, *args, is_from_cache: bool, timestamp: datetime, **kwargs) -> None:
        if isinstance(args[0], list):
            self._data = BoxList(*args, **kwargs)
        else:
            self._data = Box(*args, **kwargs)
        self._raw_data = args[0]
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
