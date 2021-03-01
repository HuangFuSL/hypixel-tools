from asyncio import Task, get_event_loop, wait
from asyncio.tasks import sleep
from base64 import standard_b64decode as b64decode
from functools import reduce
from json import JSONEncoder
from operator import and_, or_, not_, truth
from re import sub
from time import time
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple, Union

from .network import *
from .comm import BaseFilter


class AuctionOrder():
    """
    Class representing an auction. The constructer accepts a series of keyword
    
    arguments, as returned by the Hypixel API.
    """

    def __init__(self, **kwargs):
        self.bin = False
        for _ in kwargs:
            self.__setattr__(_, kwargs[_])
        if 'item_lore' in kwargs:
            self.item_lore = sub("§.", "", self.item_lore)
        self.hash = None

    def __hash__(self) -> int:
        """
        `__hash__()` implementation is required for `set` object, which supports

        `__sub__()` operator.
        """
        
        if not self.hash:
            id = getattr(self, "uuid", None)
            id = id if id else getattr(self, "auction_id", None)
            if not id:
                raise ValueError("Malformed `AuctionOrder` object")
            self.hash = reduce(
                lambda x, y: x * 16 + y,
                map(lambda _: ord(_.upper()) -
                    (48 if _.isdigit() else 55), id)
            ) + hash(id)
        return self.hash

    def __eq__(self, o) -> bool:
        try:
            return self.auction_id == o.auction_id
        except AttributeError:
            return self.uuid == o.uuid
    
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

class AuctionFilter(BaseFilter):

    @staticmethod
    def getAttributeList():
        """
        Returns a set containing all the fields for filtering
        """
        return frozenset({
            'start', 'end', 'item_name', 'item_lore', 'extra', 'category',
            'tier', 'starting_bid', 'claimed', 'claimed_bidders', 'bin',
            'highest_bid_amount', 'bids'
        })
            


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

def defaultProcessor(prev: set, current: set):
    if prev == current:
        print("No transactions")
        return None
    for _ in prev - current:
        if _.highest_bid_amount:
            print("%s sold at %d" % (_.item_name, _.highest_bid_amount))
        else:
            print("%s not sold" % (_.item_name,))
    for _ in current - prev:
        print("Auction for %s starts at %d" % (_.item_name, _.starting_bid))
    print("%d auctions remaining" % (len(current), ))


def watchAuction(
    key: str, profile: str, processor: Callable = defaultProcessor, *,
    interval: int = 30, timeout: int = -1, criteria: Optional[AuctionFilter] = None):
    loop = get_event_loop()
    loop.run_until_complete(
        _watchAuction(key, profile, processor, interval=interval, timeout=timeout, criteria=criteria)
    )

async def _watchAuction(
    key: str, profile: str, processor: Callable = defaultProcessor, *,
    interval: int = 30, timeout: int = -1, criteria: Optional[AuctionFilter] = None):
    prev, current = set(), set()
    mainFilter = AuctionFilter(
        (None, AuctionFilter(('bin', not_), ('claimed', not_), mode='and')),
        (None, AuctionFilter(('bin', truth), ('bids', not_), mode='and')),
        mode="or"
    )
    if (criteria):
        mainFilter = mainFilter.merge(criteria, mode='and')
    startTime = time()
    while timeout < 0 or startTime + timeout > time():
        del prev
        prev, current = current, mainFilter.apply(loadAuctionAPI(
            skyblock_auction(key=key, profile=profile)['auctions']
        ))
        processor(prev, current)
        await sleep(interval)

__all__ = ['AuctionOrder', 'AuctionEncoder',
           'loadAuctionPages', 'loadAuctionAPI', 'AuctionFilter', 'watchAuction']
