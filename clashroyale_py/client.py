import typing as t
from datetime import datetime, timezone
from urllib.parse import urlencode

import requests

from . import cache, errors, models, utils

# (The content of the response to the url), (if the content came from the cache), (when was the response last updated)
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
        url: str,
        timeout: t.Optional[int],
    ) -> dict:
        with self.session.request('GET', url, timeout=timeout or self.timeout) as response:
            self._verify_status_code(response.status_code)
            return response.json()

    def _verify_status_code(self, status_code: int) -> None:
        # TODO: check other status codes
        if status_code != 200:
            raise errors.UnexpectedError

    def _get_info_from_url(
        self,
        *,
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
        data = self._request(url=url, timeout=timeout)
        is_from_cache = False
        timestamp = datetime.now(timezone.utc)

        # Optionally save request to cache (if enabled)
        if self.cache and isinstance(cache_exception, KeyError) and not force_request:
            # TODO: create or update depending on the cache error
            self.cache.create(url, data, timestamp)

        return data, is_from_cache, timestamp

    def _get_model[T: models.ClashRoyaleModel](
        self,
        *,
        model_class: type[T],
        data: dict,
        is_from_cache: bool,
        timestamp: datetime
    ) -> T:
        # Check for the "items" key: when the API returns a "list"
        _data: dict | list = data.get('items', data)
        return model_class(_data, is_from_cache=is_from_cache, timestamp=timestamp, camel_killer_box=True)

    #################
    ### ENDPOINTS ###
    #################

    ######################
    ### CLAN ENDPOINTS ###
    ######################

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
        timeout: t.Optional[int] = None,
        force_request: bool = False
    ) -> models.ClashRoyaleBoxListModel:
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
            url=url, timeout=timeout, force_request=force_request
        )
        return self._get_model(
            model_class=models.ClashRoyaleBoxListModel,
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
        timeout: t.Optional[int] = None,
        force_request: bool = False
    ) -> models.ClashRoyaleBoxListModel:
        tag = utils.normalize_tag(tag)
        params = {
            'limit': limit,
            'after': after,
            'before': before
        }
        params = utils.filter_none_values(params)
        url = f'{self.api.CLAN}/{tag}/riverracelog?{urlencode(params)}'
        data, is_from_cache, timestamp = self._get_info_from_url(
            url=url, timeout=timeout, force_request=force_request
        )
        return self._get_model(
            model_class=models.ClashRoyaleBoxListModel,
            data=data,
            is_from_cache=is_from_cache,
            timestamp=timestamp
        )

    def get_clan(
        self,
        tag: str,
        timeout: t.Optional[int] = None,
        force_request: bool = False
    ) -> models.ClashRoyaleBoxModel:
        tag = utils.normalize_tag(tag)
        url = f'{self.api.CLAN}/{tag}'
        data, is_from_cache, timestamp = self._get_info_from_url(
            url=url, timeout=timeout, force_request=force_request
        )
        return self._get_model(
            model_class=models.ClashRoyaleBoxModel,
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
        timeout: t.Optional[int] = None,
        force_request: bool = False
    ) -> models.ClashRoyaleBoxListModel:
        tag = utils.normalize_tag(tag)
        params = {
            'limit': limit,
            'after': after,
            'before': before
        }
        params = utils.filter_none_values(params)
        url = f'{self.api.CLAN}/{tag}/members?{urlencode(params)}'
        data, is_from_cache, timestamp = self._get_info_from_url(
            url=url, timeout=timeout, force_request=force_request
        )
        return self._get_model(
            model_class=models.ClashRoyaleBoxListModel,
            data=data,
            is_from_cache=is_from_cache,
            timestamp=timestamp
        )

    def get_clan_current_river_race(
        self,
        tag: str,
        timeout: t.Optional[int] = None,
        force_request: bool = False
    ) -> models.ClashRoyaleBoxModel:
        tag = utils.normalize_tag(tag)
        url = f'{self.api.CLAN}/{tag}/currentriverrace'
        data, is_from_cache, timestamp = self._get_info_from_url(
            url=url, timeout=timeout, force_request=force_request
        )
        return self._get_model(
            model_class=models.ClashRoyaleBoxModel,
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
        timeout: t.Optional[int] = None,
        force_request: bool = False
    ) -> models.ClashRoyaleBoxModel:
        tag = utils.normalize_tag(tag)
        url = f'{self.api.PLAYER}/{tag}'
        data, is_from_cache, timestamp = self._get_info_from_url(
            url=url, timeout=timeout, force_request=force_request
        )
        return self._get_model(
            model_class=models.ClashRoyaleBoxModel,
            data=data,
            is_from_cache=is_from_cache,
            timestamp=timestamp
        )

    def get_player_upcoming_chests(
        self,
        tag: str,
        timeout: t.Optional[int] = None,
        force_request: bool = False
    ) -> models.ClashRoyaleBoxListModel:
        tag = utils.normalize_tag(tag)
        url = f'{self.api.PLAYER}/{tag}/upcomingchests'
        data, is_from_cache, timestamp = self._get_info_from_url(
            url=url, timeout=timeout, force_request=force_request
        )
        return self._get_model(
            model_class=models.ClashRoyaleBoxListModel,
            data=data,
            is_from_cache=is_from_cache,
            timestamp=timestamp
        )

    def get_player_battle_log(
        self,
        tag: str,
        timeout: t.Optional[int] = None,
        force_request: bool = False
    ) -> models.ClashRoyaleBoxListModel:
        tag = utils.normalize_tag(tag)
        url = f'{self.api.PLAYER}/{tag}/battlelog'
        data, is_from_cache, timestamp = self._get_info_from_url(
            url=url, timeout=timeout, force_request=force_request
        )
        # This endpoint return a list rather than a dict with "items" key and a list value.
        # Because of this, we make the dict to pass to the "_get_model" method
        data = {'items': data}
        return self._get_model(
            model_class=models.ClashRoyaleBoxListModel,
            data=data,
            is_from_cache=is_from_cache,
            timestamp=timestamp
        )

    #######################
    ### CARDS ENDPOINTS ###
    #######################

    def get_cards(
        self,
        limit: t.Optional[int] = None,
        after: t.Optional[str] = None,
        before: t.Optional[str] = None,
        timeout: t.Optional[int] = None,
        force_request: bool = False
    ) -> models.ClashRoyaleBoxListModel:
        params = {
            'limit': limit,
            'after': after,
            'before': before
        }
        params = utils.filter_none_values(params)
        url = f'{self.api.CARDS}?{urlencode(params)}'
        data, is_from_cache, timestamp = self._get_info_from_url(
            url=url, timeout=timeout, force_request=force_request
        )
        # This endpoint has a "items" key. This makes the "_get_model" to use only its value as data.
        # But this endpoint also has a "supportItems" key that is important.
        # Because of this, we need to merge the two keys so the "items" key will have all the values
        data = {'items': data['items'] + data['supportItems']}
        return self._get_model(
            model_class=models.ClashRoyaleBoxListModel,
            data=data,
            is_from_cache=is_from_cache,
            timestamp=timestamp
        )

    #############################
    ### TOURNAMENTS ENDPOINTS ###
    #############################

    def get_tournaments(
        self,
        name: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        after: t.Optional[str] = None,
        before: t.Optional[str] = None,
        timeout: t.Optional[int] = None,
        force_request: bool = False
    ) -> models.ClashRoyaleBoxListModel:
        params = {
            'name': name,
            'limit': limit,
            'after': after,
            'before': before
        }
        params = utils.filter_none_values(params)
        url = f'{self.api.TOURNAMENT}?{urlencode(params)}'
        data, is_from_cache, timestamp = self._get_info_from_url(
            url=url, timeout=timeout, force_request=force_request
        )
        return self._get_model(
            model_class=models.ClashRoyaleBoxListModel,
            data=data,
            is_from_cache=is_from_cache,
            timestamp=timestamp
        )

