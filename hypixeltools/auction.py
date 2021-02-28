from asyncio import Task, get_event_loop, wait
from base64 import standard_b64decode as b64decode
from functools import reduce
from json import JSONEncoder
from operator import or_
from re import sub
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .network import *


class AuctionOrder():
    """
    Class representing an auction. The constructer accepts a series of keyword
    
    arguments, as returned by the Hypixel API.
    """

    def __init__(self, **kwargs):
        for _ in kwargs:
            self.__setattr__(_, kwargs[_])
        if 'item_lore' in kwargs:
            self.item_lore = sub("§.", "", self.item_lore)

    def __hash__(self) -> int:
        """
        `__hash__()` implementation is required for `set` object, which supports

        `__sub__()` operator.
        """
        return reduce(
            lambda x, y: x * 16 + y,
            map(lambda _: ord(_.upper()) - (48 if _.isdigit() else 55), self.uuid)
        ) + hash(self.uuid)
    
    def __repr__(self) -> str:
        try:
            return "<%s at %d>" % (self.extra, self.starting_bid)
        except AttributeError:
            return None

    def __str__(self) -> str:
        try:
            return ':\n'.join([self.item_name, self.item_lore])
        except AttributeError:
            return None
    
    def dealPrice(self) -> Optional[Union[float, int]]:
        return self.highest_bid_amount if self.highest_bid_amount else None

    def getItemByte(self) -> bytes:
        """
        Decode the item data, which is base64-encoded.
        """
        return b64decode(self.item_bytes['data'])


class AuctionEncoder(JSONEncoder):
    """
    Encoder for JSON_serializing an `AuctionOrder` object
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def default(self, o: Any) -> Any:
        if isinstance(o, AuctionOrder):
            return o.__dict__
        else:
            return super().default(o)

def loadAuctionAPI(response) -> Union[Set[AuctionOrder], AuctionOrder]:
    """
    Load the auction data directly from the API response.

    Parameters: `list` or `dict` object

    When the parameter is a `list` object, the returned value is a `set` object,

    otherwise it is an `AuctionOrder` object.
    """
    if isinstance(response, dict):
        return AuctionOrder(**response)
    elif isinstance(response, list):
        return {AuctionOrder(**_) for _ in response}
    else:
        raise ValueError("Invalid parameter.")

def loadAuctionPages(key: str, *pageRange: Tuple[int]) -> Set[AuctionOrder]:
    """
    Get all of the active auctions in the game asynchronously.
    """
    start, end, step = 0, -1, 1
    if len(pageRange) == 0:
        pass
    elif len(pageRange) == 1:
        end, = pageRange
    elif len(pageRange) == 2:
        start, end = pageRange
    elif len(pageRange) == 3:
        start, end, step = pageRange
    else:
        raise ValueError("loadAuctionPages() accepts up to 4 parameters.")

    firstPage = skyblock_auctions(key=key, page=start)
    if end < 0 or end > firstPage['totalPages']:
        end = firstPage['totalPages']
    ret: List[Dict] = []
    tasks: List[Task] = [
        Task(async_skyblock_auctions(key=key, page=i))
        for i in range(start + step, end, step)
    ]

    loop = get_event_loop()
    loop.run_until_complete(wait(tasks))

    for task in tasks:
        ret.append(task.result()['auctions'])

    ret.append(firstPage['auctions'])
    return reduce(or_, map(loadAuctionAPI, ret))
    

__all__ = ['AuctionOrder', 'AuctionEncoder',
           'loadAuctionPages', 'loadAuctionAPI']
