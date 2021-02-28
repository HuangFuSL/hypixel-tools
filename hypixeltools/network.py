import json
from typing import Callable

import requests

root_URL = "http://api.hypixel.net/"
mojang_URL = "https://sessionserver.mojang.com/session/minecraft/profile/"
arg_parser = lambda **kwargs: "?" + \
    "&".join([_ + "=" + str(kwargs[_]) for _ in kwargs])
api_content = {}
asyncapi_content = {}
interfaces = []

class IllegalArgumentError(Exception):

    def __init__(self, obj):
        super().__init__(obj)

    def __str__(self) -> str:
        return super().__str__()

def api(e: Callable) -> Callable:
    """
    Decorator for Hypixel API methods.
    """
    
    name = e()
    def ret(**kwargs):
        api_name = name
        ret = json.loads(requests.get(root_URL + api_name + arg_parser(**kwargs)).content)
        if ret['success']:
            return ret
        else:
            raise IllegalArgumentError(ret['cause'])

    ret.__doc__ = e.__doc__
    api_content[name] = ret
    interfaces.append(name.replace("/", "_"))
    return ret


async def get_wrapper(url, params = None, **kwargs):
    return requests.get(url, params, **kwargs)

def asyncapi(e: Callable) -> Callable:
    """
    async version of the decorator
    """

    name = e()
    async def ret(**kwargs):
        api_name = name
        resp = json.loads((await get_wrapper(root_URL + api_name + arg_parser(**kwargs))).content)
        if resp['success']:
            return resp
        else:
            raise IllegalArgumentError(resp['cause'])

    asyncapi_content[name] = ret
    interfaces.append("async_" + name.replace("/", "_"))
    return ret


@api
def watchdogstats():
    """
    Returns some statistics about Watchdog & bans.

    Parameters: `key`

    Example Response:

    ```json
    {
        'success': True,
        'watchdog_lastMinute': 2,
        'staff_rollingDaily': 3227,
        'watchdog_total': 6315204,
        'watchdog_rollingDaily': 6534,
        'staff_total': 2227861
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/watchdogstats.md
    """
    return "watchdogstats"
@asyncapi
def async_watchdogstats():
    return "watchdogstats"


@api
def status():
    """
    Returns online status information for given player, including game, mode and map when available.

    Players can disable this endpoint via in-game settings. When done so the API will return as if the player is offline.

    Parameters: `key`, `uuid`

    Example Response:

    ```json
    {
        'success': True,
        'session': {
            'online': True,
            'gameType': 'SKYBLOCK',
            'mode': 'hub'
        }
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/status.md
    """
    return "status"


@asyncapi
def async_status():
    return "status"


def resources(**kwargs):
    """
    Provides an endpoint to retrieve resources which don't change often. This does not require an API key.

    All resources return lastUpdated field which is a Unix milliseconds value of when the file was last updated. Some files, such as for SkyBlock will also return the game version they were generated for.

    Parameters: `resource`

    Supported Values:

    * achievements
    * challenges
    * quests
    * guilds/achievements
    * guilds/permissions
    * skyblock/collections
    * skyblock/skills

    Example Response:

    ```json
    {
        'success': True,
        'lastUpdated': 1570754198669,
        'permissions': [
            {
                'en_us': {
                    'name': 'Modify Guild Name',
                    'description': "Change the guild's name.",
                    'item': {
                        'name': 'name_tag'
                    }
                }
            },
            ...
        ]
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/resources.md
    """
    api_name = "resources"
    ret = json.loads(requests.get(
    root_URL + api_name + "/" + kwargs['resource']).content)
    if ret['success']:
        return ret
    else:
        raise IllegalArgumentError(ret['cause'])


@api
def recentgames():
    """
    Returns recent games of a player. A maximum of 100 games are returned and recent games are only stored for up to 3 days at this time.

    Players can disable this endpoint via in-game settings. When done so the API will return as if there is no games.

    Parameters: `key`, `uuid`

    Example Response:

    ```json
    {
        'success': True,
        'games': [
            {
                'date': 1614387593861,
                'gameType': 'ARCADE',
                'mode': 'DEFENDER',
                'map': 'Creeper Attack',
                'ended': 1614388408163
            },
            ...
        ]
    }

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/recentGames.md
    ```
    """
    return "recentgames"


@asyncapi
def async_recentgames():
    return "recentgames"

@api
def playercount():
    """
    Returns current player count.

    This is also now included in the gameCounts method.

    Parameters: `key`

    Example Response:

    ```json
    {
        'success': True,
        'playerCount': 123409
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/playerCount.md
    """
    return "playercount"


@asyncapi
def async_playercount():
    return "playercount"

@api
def player():
    """
    Returns a player's data, such as game stats.

    Parameters: `key`, `uuid`

    Example Response:

    ```json
    {
        'success': True,
        'player': {
            '_id': '************************', // Hypixel ID
            'uuid': '********************************', // The Minecraft UUID
            'displayname': '****', // Minecraft account name
            'firstLogin': 1581242093516,
            'knownAliases': ['****'],
            'knownAliasesLower': ['****'],
            'lastLogin': 1614477680870,
            'playername': '****',
            'achievementsOneTime': [
                'general_first_join',
                ...
            ],
            'achievementPoints': 930,
            'stats': {
                'Pit': { // Game name as key
                    ... // Game stastics
                },
                ...
            },
            'mcVersionRp': '1.16.5',
            'mostRecentGameType': 'PROTOTYPE'
        }
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/player.md
    """
    return "player"


@asyncapi
def async_player():
    return "player"

@api
def leaderboards():
    """
    Returns a list of the official leaderboards and their current standings for games on the network.

    Parameters: `key`

    ```json
    {
        'success': True,
        'leaderboards': {
            'PROTOTYPE': [], // Catrgorized by lobby type
            'TNTGAMES': [
                {
                    'path': 'wins_tntrun', // Categorized by sub-game
                    'prefix': 'Overall', 
                    'title': 'TNT Run Wins', 
                    'location': '-2554,57,715', 
                    'count': 10,
                    'leaders': [
                        'aed8deec-8c35-4187-8a79-ba72ab29076d', // Players on the leadboard
                        ...
                    ]
                }, 
                ...
            ],
            ...
        }
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/leaderboards.md
    """
    return "leaderboards"


@asyncapi
def async_leaderboards():
    return "leaderboards"

@api
def key():
    """
    Returns information regarding given key.

    Parameters: `key`

    Example Response:

    ```json
    {
        'success': True,
        'record': {
            'key': '********-****-****-****-************',
            'owner': '********-****-****-****-************',
            'limit': 120,
            'queriesInPastMin': 1,
            'totalQueries': 277984
        }
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/key.md
    """
    return "key"


@asyncapi
def async_key():
    return "key"

@api
def guild():
    """
    Returns information about given guild.

    For a JSON list of Guild achievements and a JSON list of Guild permissions, please refer to `resource()` method

    Parameters: `key`, `id` (Guild ID returned by `findguild()` method), `player`, `name` (Guild name)

    A detailed explanation of each field can be found at https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/guild.md
    """
    return "guild"


@asyncapi
def async_guild():
    return "guild"

@api
def gamecounts():
    """
    Returns the current player count along with the player count of each public game + mode on the server.

    Due to the large amount of modes and that they can change at anytime we don't currently have a friendly
    
    list of mode keys to clean names. This may be added at a later date.

    Parameters: `key`

    Example Response:

    ```json
    {
        'success': True,
        'games': {
            'MAIN_LOBBY': {'players': 951},
            'TOURNAMENT_LOBBY': {'players': 31},
            'LEGACY': {
                'players': 419,
                'modes': {
                    'ARENA': 9, 
                    ...
                }
            }, 
            ...    
        },
        'playerCount': 123909
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/gameCounts.md
    """
    return "gamecounts"


@asyncapi
def async_gamecounts():
    return "gamecounts"

@api
def friends():
    """
    Returns friendships for given player.

    Parameters: `key`, `uuid`

    Example Response:

    ```json
    {
        'success': True,
        'records': [
            {
                '_id': '************************',
                'uuidSender': '********************************',
                'uuidReceiver': '********************************',
                'started': 1595912821091
            },
            ...
        ]
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/friends.md
    """
    return "friends"


@asyncapi
def async_friends():
    return "friends"

@api
def findguild():
    """
    Returns the id of the requested guild.

    Parameters: `key`, `byName`, `byUuid`

    Example Response:

    ```json
    {
        "success": true,
        "guild": "************************"
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/findGuild.md
    """
    return "findguild"


@asyncapi
def async_findguild():
    return "findguild"

@api
def boosters():
    """
    Returns list of boosters.

    Parameters: `key`

    Example Response:

    ```json
    {
        "success": true,
        "boosters": [
            {
                "_id": "************************",
                "purchaserUuid": "********************************",
                "amount": 2, // Multiplier
                "originalLength": 3600,
                "length": 3595, // Length remaining
                "gameType": 24, // GameType ID
                "dateActivated": 1545244519133,
                "stacked": true
            },
            {
                "_id": "************************",
                "purchaserUuid": "********************************",
                "amount": 2.2,
                "originalLength": 3600,
                "length": 2074,
                "gameType": 13,
                "dateActivated": 1590842991659,
                "stacked": [
                    "********-****-****-****-************",
                    ...
                ]
            }
        ],
        "boosterState": {
            "decrementing": true
        }
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/boosters.md
    """
    return "boosters"


@asyncapi
def async_boosters():
    return "boosters"

@api
def skyblock_auction():
    """
    Returns SkyBlock auctions by either player, profile or auction uuid.
    Only "active" auctions are returned, these are auctions that are still open or that have not had all bids/items claimed.

    Parameters: `key`, `player`, `profile`, `uuid`

    Example Response: 

    ```json
    {
        "success": true,
        "auctions": [
            {
                "_id": "************************",
                "uuid": "********************************",
                "auctioneer": "********************************",
                "profile_id": "********************************",
                "coop": [
                    "********************************",
                    ...
                ],
                "start": 1573760802637,
                "end": 1573761102637,
                "item_name": "Azure Bluet",
                "item_lore": "§f§lCOMMON",
                "extra": "Azure Bluet Red Rose",
                "category": "blocks",
                "tier": "COMMON",
                "starting_bid": 1,
                "item_bytes": {
                    "type": 0,
                    "data": ...
                },
                "claimed": true,
                "claimed_bidders": [],
                "highest_bid_amount": 7607533,
                "bids": [
                    {
                        "auction_id": "********************************",
                        "bidder": "********************************",
                        "profile_id": "********************************",
                        "amount": 7607533,
                        "timestamp": 1573760824844
                    },
                    ...
                ]
            }
        ]
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/skyblock/auction.md
    """
    return "skyblock/auction"


@asyncapi
def async_skyblock_auction():
    return "skyblock/auction"

@api
def skyblock_auctions():
    """
    Returns SkyBlock auctions that are currently active in the in-game Auction House. This method uses pagination due to the amount of results returned. Each page will return up to 1,000 results.

    Parameters: `key`, `page`

    Example Response:

    ```json
    {
        "success": true,
        "page": 0,
        "totalPages": 32,
        "totalAuctions": 31267,
        "lastUpdated": 1571065561345,
        "auctions": [
            ... // Same as `skyblock_auction` method
        ]
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/skyblock/auctions.md
    """
    return "skyblock/auctions"


@asyncapi
def async_skyblock_auctions():
    return "skyblock/auctions"

@api
def skyblock_auctions_ended():
    """
    Returns SkyBlock auctions which ended in the last 60 seconds (More precisely, whatever time is defined in the "Cache-Control" header of the response).

    Parameters: `key`

    Example Response:

    ```json
    {
        "success": true,
        "lastUpdated": 1607456463916,
        "auctions": [
            {
                "auction_id": "********************************",
                "seller": "********************************",
                "seller_profile": "********************************",
                "buyer": "********************************",
                "timestamp": 1607456400329,
                "price": 190000,
                "bin": true,
                "item_bytes": ...
            },
            ...
        ]
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/skyblock/auctions_ended.md
    """
    return "skyblock/auctions_ended"


@asyncapi
def async_skyblock_auctions_ended():
    return "skyblock/auctions_ended"

@api
def skyblock_bazaar():
    """
    Returns the list of products along with their sell summary, buy summary and quick status.

    Parameters: `key`

    Example Response:

    ```json
    {
        "success": true,
        "lastUpdated": 1590854517479,
        "products": {
            "INK_SACK:3": {
                "product_id": "INK_SACK:3",
                "sell_summary": [
                    {"amount": 20569, "pricePerUnit": 4.2, "orders": 1},
                    ...
                ],
                "buy_summary": [
                    { "amount": 640, "pricePerUnit": 4.8, "orders": 1},
                    ...
                ],
                "quick_status": {
                    "productId": "INK_SACK:3",
                    "sellPrice": 4.2,
                    "sellVolume": 409855,
                    "sellMovingWeek": 8301075,
                    "sellOrders": 11,
                    "buyPrice": 4.99260315136572,
                    "buyVolume": 1254854,
                    "buyMovingWeek": 5830656,
                    "buyOrders": 85
                }
            }
        }
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/skyblock/bazaar.md
    """
    return "skyblock/bazaar"


@asyncapi
def async_skyblock_bazaar():
    return "skyblock/bazaar"

@api
def skyblock_news():
    """
    Returns SkyBlock news, including a title, description and a thread.

    Parameters: `key`

    Example Response:

    ```json
    {
        'success': True,
        'items': [
            {
                'item': {'material': 'DIAMOND_PICKAXE'},
                'link': 'https://hypixel.net/threads/3749492/',
                'text': '15th January 2021',
                'title': 'SkyBlock v0.11'
            }, 
            ...
        ]
    }
    ```

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/skyblock/news.md
    """
    return "skyblock/news"


@asyncapi
def async_skyblock_news():
    return "skyblock/news"

@api
def skyblock_profile():
    """
    Returns a SkyBlock profile's data, such as stats, objectives etc. The data returned can differ depending on the players in-game API settings.

    Parameters: `key`, `profile`

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/skyblock/profile.md
    """
    return "skyblock/profile"


@asyncapi
def async_skyblock_profile():
    return "skyblock/profile"

@api
def skyblock_profiles():
    """
    Returns an array SkyBlock profile's data, such as stats, objectives etc.
    
    The data returned can differ depending on the players in-game API settings.
    
    The request takes a player UUID.

    Parameters: `key`, `uuid`

    https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/skyblock/profiles.md
    """
    return "skyblock/profiles"


@asyncapi
def async_skyblock_profiles():
    return "skyblock/profiles"

__all__ = interfaces.copy()
