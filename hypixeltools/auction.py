from asyncio import Task, get_event_loop, wait
from base64 import standard_b64decode as b64decode
from functools import reduce
from json import JSONEncoder
from operator import or_
from re import sub
from typing import Any, Dict, List

from .network import *


class AuctionOrder():

    def __init__(self, **kwargs):
        for _ in kwargs:
            self.__setattr__(_, kwargs[_])
        if 'item_lore' in kwargs:
            self.item_lore = sub("§.", "", self.item_lore)

    def __hash__(self) -> int:
        return reduce(
            lambda x, y: x * 16 + y,
            map(lambda _: ord(_.upper()) - (48 if _.isdigit() else 55), self.uuid)
        ) + hash(self.uuid)
    
    def __repr__(self):
        try:
            return "<%s at %d>" % (self.extra, self.starting_bid)
        except AttributeError:
            return None

    def __str__(self):
        try:
            return ':\n'.join([self.item_name, self.item_lore])
        except AttributeError:
            return None
    
    def dealPrice(self):
        return self.highest_bid_amount if self.highest_bid_amount else None

    def getItemByte(self):
        return b64decode(self.item_bytes['data'])


class AuctionEncoder(JSONEncoder):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def default(self, o: Any) -> Any:
        if isinstance(o, AuctionOrder):
            return o.__dict__
        else:
            return super().default(o)

def loadFromAPI(response):
    if isinstance(response, dict):
        return AuctionOrder(**response)
    elif isinstance(response, list):
        return {AuctionOrder(**_) for _ in response}
    else:
        raise ValueError("Invalid parameter.")

def loadFullPage(key: str):
    firstPage = skyblock_auctions(key=key, page=0)
    pageCount = firstPage['totalPages']
    ret: List[Dict] = []
    tasks: List[Task] = [
        Task(async_skyblock_auctions(key=key, page=i))
        for i in range(1, pageCount)
    ]

    loop = get_event_loop()
    loop.run_until_complete(wait(tasks))

    for task in tasks:
        ret.append(task.result()['auctions'])

    ret.append(firstPage['auctions'])
    return reduce(or_, map(loadFromAPI, ret))
    
