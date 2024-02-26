from cache import SqliteCacheStorage
from client import Client
import time

CLAN_TAG = '#2QPGV2VY'
TOKEN = 'YOUR_TOKEN_HERE'

# Create the cache and the client
cache = SqliteCacheStorage('my_cache.db', expiration_time_in_minutes=1)
client = Client(TOKEN, cache_storage=cache)

# Get a bunch of info
# Will make requests from the API and save them on the cache
start = time.time()
client.get_clan(CLAN_TAG)
client.get_clan_current_river_race(CLAN_TAG)
client.get_clan_members(CLAN_TAG)
client.get_clans(CLAN_TAG)
client.get_clan_river_race_log(CLAN_TAG)
end = time.time()
print(f'API requests: {end - start}')

# Make requests again. This time they will come from the cache
start = time.time()
client.get_clan(CLAN_TAG)
client.get_clan_current_river_race(CLAN_TAG)
client.get_clan_members(CLAN_TAG)
client.get_clans(CLAN_TAG)
client.get_clan_river_race_log(CLAN_TAG)
end = time.time()
print(f'CACHE requests: {end - start}')

# Wait the for the cache to expire
time.sleep(65)
# Now that the cache is expired, will make requests from the API again and update the cache
start = time.time()
client.get_clan(CLAN_TAG)
client.get_clan_current_river_race(CLAN_TAG)
client.get_clan_members(CLAN_TAG)
client.get_clans(CLAN_TAG)
client.get_clan_river_race_log(CLAN_TAG)
end = time.time()
print(f'API requests (again): {end - start}')