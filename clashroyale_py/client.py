import typing as t
from datetime import datetime, timezone
from urllib.parse import urlencode

import requests

from . import cache, errors, models, utils

# The content of the response to the url, if the content came from the cache, when was the response last updated
type InfoFromURL = tuple[dict, bool, datetime]


class API:
    BASE = 'https://api.clashroyale.com/v1'
    PLAYER = BASE + '/players'
    CLAN = BASE + '/clans'
    TOURNAMENT = BASE + '/tournaments'
    CARDS = BASE + '/cards'
    LOCATIONS = BASE + '/locations'


class Client:
    def __init__(
        self,
        token: str,
        timeout: int = 10,
        cache_storage: t.Optional[cache.CacheStorage] = None,
        session: t.Optional[requests.Session] = None
    ) -> None:
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'User-Agent': 'python-clashroyale-client (fourjr/kyb3r) ',
        }
        self.timeout = timeout
        self.cache = cache_storage
        self.session = session or requests.Session()
        self.session.headers.update(self.headers)
        self.api = API

    def _request(
        self,
        *,
        method: str,
        url: str,
        timeout: t.Optional[int],
    ) -> dict:
        with self.session.request(method, url, timeout=timeout or self.timeout) as response:
            self._verify_status_code(response.status_code)
            return response.json()

    def _verify_status_code(self, status_code: int) -> None:
        # TODO: check other status codes
        if status_code != 200:
            raise errors.UnexpectedError

    def _get_info_from_url(
        self,
        *,
        method: str,
        url: str,
        timeout: t.Optional[int],
        force_request: bool,
    ) -> InfoFromURL:
        cache_exception = None
        # Attempt to get data from cache (if enabled)
        # if force_request is True, forces a request instead of using cache
        if self.cache and not force_request:
            try:
                data, timestamp = self.cache.read(url)
                if data and timestamp:
                    is_from_cache = True
                    return data, is_from_cache, timestamp
            except Exception as error:
                cache_exception = error

        # If there is a cache error or if it is not enabled, fetch from request
        data = self._request(method=method, url=url, timeout=timeout)
        is_from_cache = False
        timestamp = datetime.now(timezone.utc)

        # Optionally save request to cache (if enabled)
        if self.cache and isinstance(cache_exception, KeyError) and not force_request:
            # TODO: create or update depending on the cache error
            self.cache.create(url, data, timestamp)

        return data, is_from_cache, timestamp

    def _get_model(
        self,
        *,
        model,
        data,
        is_from_cache,
        timestamp
    ) -> models.BaseAttrDict | list[models.BaseAttrDict] | str:
        # TODO: refactor this function
        # TODO: Add dynamic return value based on the model parameter
        response = None
        if model is None and isinstance(data, list):
            model = models.BaseAttrDict
        else:
            model = models.Refreshable

        if isinstance(data, str):
            # version endpoint, not feasible to add refresh functionality.
            return data
        if isinstance(data, list):
            return (
                models.RefreshableList(self, data, is_from_cache, timestamp, response)
                if all(isinstance(x, str) for x in data)
                else [
                    model(self, d, response, cached=is_from_cache, ts=timestamp)
                    for d in data
                ]
            )
        if 'items' not in data:
            return model(self, data, response, cached=is_from_cache, ts=timestamp)
        if data.get('paging'):
            return models.PaginatedAttrDict(self, data, response, model, cached=is_from_cache, ts=timestamp)
        return self._get_model(
            model=model,
            data=data['items'],
            is_from_cache=is_from_cache,
            timestamp=timestamp
        )

    #################
    ### ENDPOINTS ###
    #################
    
    ######################
    ### CLAN ENDPOINTS ###
    ######################
    
    # TODO: add return types to the endpoints

    def get_clans(
        self,
        name: t.Optional[str] = None,
        location_id: t.Optional[int] = None,
        min_members: t.Optional[int] = None,
        max_members: t.Optional[int] = None,
        min_score: t.Optional[int] = None,
        limit: t.Optional[int] = None,
        after: t.Optional[str] = None,
        before: t.Optional[str] = None,
        timeout: t.Optional[int] = None
    ):
        params = {
            'name': name,
            'locationId': location_id,
            'minMembers': min_members,
            'maxMembers': max_members,
            'minScore': min_score,
            'limit': limit,
            'after': after,
            'before': before
        }
        params = utils.filter_none_values(params)
        url = f'{self.api.CLAN}?{urlencode(params)}'  # with params
        data, is_from_cache, timestamp = self._get_info_from_url(
            method='GET', url=url, timeout=timeout, force_request=False
        )
        return self._get_model(
            model=models.PartialClan,
            data=data,
            is_from_cache=is_from_cache,
            timestamp=timestamp
        )

    def get_clan_river_race_log(
        self,
        tag: str,
        limit: t.Optional[int] = None,
        after: t.Optional[str] = None,
        before: t.Optional[str] = None,
        timeout: t.Optional[int] = None
    ):
        tag = utils.normalize_tag(tag)
        params = {
            'limit': limit,
            'after': after,
            'before': before
        }
        params = utils.filter_none_values(params)
        url = f'{self.api.CLAN}/{tag}/riverracelog?{urlencode(params)}'
        data, is_from_cache, timestamp = self._get_info_from_url(
            method='GET', url=url, timeout=timeout, force_request=False
        )
        return self._get_model(
            model=None,
            data=data,
            is_from_cache=is_from_cache,
            timestamp=timestamp
        )

    def get_clan(
        self,
        tag: str,
        timeout: t.Optional[int] = None
    ):
        tag = utils.normalize_tag(tag)
        url = f'{self.api.CLAN}/{tag}'
        data, is_from_cache, timestamp = self._get_info_from_url(
            method='GET', url=url, timeout=timeout, force_request=False
        )
        return self._get_model(
            model=models.FullClan,
            data=data,
            is_from_cache=is_from_cache,
            timestamp=timestamp
        )

    def get_clan_members(
        self,
        tag: str,
        limit: t.Optional[int] = None,
        after: t.Optional[str] = None,
        before: t.Optional[str] = None,
        timeout: t.Optional[int] = None
    ):
        tag = utils.normalize_tag(tag)
        params = {
            'limit': limit,
            'after': after,
            'before': before
        }
        params = utils.filter_none_values(params)
        url = f'{self.api.CLAN}/{tag}/members?{urlencode(params)}'
        data, is_from_cache, timestamp = self._get_info_from_url(
            method='GET', url=url, timeout=timeout, force_request=False
        )
        return self._get_model(
            model=None,
            data=data,
            is_from_cache=is_from_cache,
            timestamp=timestamp
        )

    def get_clan_current_river_race(
        self,
        tag: str,
        timeout: t.Optional[int] = None
    ):
        tag = utils.normalize_tag(tag)
        url = f'{self.api.CLAN}/{tag}/currentriverrace'
        data, is_from_cache, timestamp = self._get_info_from_url(
            method='GET', url=url, timeout=timeout, force_request=False
        )
        return self._get_model(
            model=None,
            data=data,
            is_from_cache=is_from_cache,
            timestamp=timestamp
        )

    #########################
    ### PLAYERS ENDPOINTS ###
    #########################
    
    def get_player(
        self,
        tag: str,
        timeout: t.Optional[int] = None
    ):
        tag = utils.normalize_tag(tag)
        url = f'{self.api.PLAYER}/{tag}'
        data, is_from_cache, timestamp = self._get_info_from_url('GET', url, timeout, None)
        return self._get_model(
            model=models.FullPlayer,
            data=data,
            is_from_cache=is_from_cache,
            timestamp=timestamp
        )