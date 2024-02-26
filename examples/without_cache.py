from cache import SqliteCacheStorage
from client import Client
import time

CLAN_TAG = '#2QPGV2VY'
TOKEN = 'YOUR_TOKEN_HERE'

# Create the client
client = Client(TOKEN)

# Get a bunch of info
# Will make requests from the API
start = time.time()
client.get_clan(CLAN_TAG)
client.get_clan_current_river_race(CLAN_TAG)
client.get_clan_members(CLAN_TAG)
client.get_clans(CLAN_TAG)
client.get_clan_river_race_log(CLAN_TAG)
end = time.time()
print(f'API requests: {end - start}')

# Make requests again just because
start = time.time()
client.get_clan(CLAN_TAG)
client.get_clan_current_river_race(CLAN_TAG)
client.get_clan_members(CLAN_TAG)
client.get_clans(CLAN_TAG)
client.get_clan_river_race_log(CLAN_TAG)
end = time.time()
print(f'API requests (again): {end - start}')