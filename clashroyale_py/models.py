from box import Box, BoxList

__all__ = [
    'BaseAttrDict', 'PaginatedAttrDict', 'Refreshable',
    'PartialClan', 'PartialPlayer', 'PartialPlayerClan',
    'Member', 'FullPlayer', 'FullClan', 'RefreshableList'
]


class BaseAttrDict:
    """This class is the base class for all models,
    its a wrapper around the `python-box`_ which allows
    access to data via dot notation, in this case, API
    data will be accessed using this class.
    This class should not normally be used by the user
    since its a base class for the actual models returned from the client.
    """

    def __init__(self, client, data, response, cached=False, ts=None):
        self.client = client
        self.response = response
        self.from_data(data, cached, ts, response)

    def from_data(self, data, cached, ts, response):
        self.cached = cached
        self.last_updated = ts
        self.raw_data = data
        self.response = response
        if isinstance(data, list):
            self._boxed_data = BoxList(
                data, camel_killer_box=True
            )
        else:
            self._boxed_data = Box(
                data, camel_killer_box=True
            )
        return self

    def __getattr__(self, attr):
        try:
            return getattr(self._boxed_data, attr)
        except AttributeError:
            try:
                return super().__getattr__(attr)
            except AttributeError:
                return None

    def __getitem__(self, item):
        try:
            return getattr(self._boxed_data, item)
        except AttributeError:
            raise KeyError('No such key: {}'.format(item))

    def __repr__(self):
        _type = self.__class__.__name__
        return "<{}: {}>".format(_type, self.raw_data)


class PaginatedAttrDict(BaseAttrDict):
    """Mixin class to allow for the paginated endpoints to be iterable"""

    def __init__(self, client, data, response, model, cached=False, ts=None):
        self.cursor = {'after': data['paging']['cursors'].get(
            'after'), 'before': data['paging']['cursors'].get('before')}
        self.client = client
        self.response = response
        self.model = model
        self.raw_data = [model(client, d, response, cached=cached, ts=ts)
                         for d in data['items']]

    def __len__(self):
        return len(self.raw_data)

    def __getattr__(self, attr):
        try:
            return self.raw_data[attr]
        except AttributeError:
            try:
                return super().__getattr__(attr)
            except AttributeError:
                return None

    def __getitem__(self, item):
        try:
            return self.raw_data[item]
        except AttributeError:
            raise KeyError('No such key: {}'.format(item))

    def __iter__(self):
        while True:
            index = 0
            for _ in range(index, len(self.raw_data)):
                yield self.raw_data[index]
                index += 1
            if not self.update_data():
                break

    def to_json(self):
        return self.raw_data

    def update_data(self):
        """Adds the NEXT data in the raw_data dictionary.
        Returns True if data is added.
        Returns False if data is not added"""

        if self.cursor['after']:
            data, cached, ts, response = self.client._request(
                self.response.url, timeout=None, after=self.cursor['after'])
            self.cursor = {'after': data['paging']['cursors'].get(
                'after'), 'before': data['paging']['cursors'].get('before')}
            self.raw_data += [self.model(self.client, d, response,
                                         cached=cached, ts=ts) for d in data['items']]
            return True

        return False

    def all_data(self):
        """Loops through and adds all data to the raw_data

        This has a chance to get 429 RateLimitError"""
        while self.update_data():
            pass


class Refreshable(BaseAttrDict):
    """Mixin class for re requesting data from
    the api for the specific model.
    """

    def refresh(self):
        """sync refresh the data."""
        data, cached, ts, response = self.client._request(
            self.response.url, timeout=None, refresh=True)
        return self.from_data(data, cached, ts, response)


class PartialClan(BaseAttrDict):
    def get_clan(self):
        """(a)sync function to return clan."""
        try:
            return self.client.get_clan(self.clan.tag)
        except AttributeError:
            try:
                return self.client.get_clan(self.tag)
            except AttributeError:
                raise ValueError('This player does not have a clan.')


class PartialTournament(BaseAttrDict):
    def get_tournament(self):
        return self.client.get_player(self.tag)


class PartialPlayer(BaseAttrDict):
    def get_player(self):
        """(a)sync function to return player."""
        return self.client.get_player(self.tag)


class PartialPlayerClan(PartialClan, PartialPlayer):
    """Brief player model,
    does not contain full data, non refreshable.
    """
    pass


class Member(PartialPlayer):
    """A clan member model,
    keeps a reference to the clan object it came from.
    """

    def __init__(self, clan, data, response):
        self.clan = clan
        super().__init__(clan.client, data, response)


class FullPlayer(Refreshable, PartialClan):
    """A Clash Royale player model."""
    pass


class FullClan(Refreshable):
    """A Clash Royale clan model, full data + refreshable."""

    def from_data(self, data, cached, ts, response):
        super().from_data(data, cached, ts, response)
        self.members = [Member(self, m, self.response)
                        for m in data.get('member_list', [])]


class RefreshableList(list, Refreshable):
    def __init__(self, client, data, cached, ts, response):
        self.client = client
        self.from_data(data, cached, ts, response)

    def from_data(self, data, cached, ts, response):
        self.cached = cached
        self.last_updated = ts
        self.response = response
        super().__init__(data)
        return self

    @property
    def url(self):
        return '{}/endpoints'.format(self.client.api.BASE)
