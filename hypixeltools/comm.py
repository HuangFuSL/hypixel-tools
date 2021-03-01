from abc import abstractmethod, abstractstaticmethod
from operator import and_, or_
from typing import Iterable

class BaseFilter():

    @abstractstaticmethod
    def getAttributeList() -> frozenset:
        raise NotImplementedError()

    def __init__(self, *args, mode: str = 'and'):
        self.filter = args
        self.mode = mode
        if mode not in ['and', 'or']:
            raise ValueError(
                "Filter mode should be either 'and' or 'or', got %s" % (mode,)
            )
        for arg, func in self.filter:
            if not callable(func):
                raise ValueError(str(type(func)) + " object is not callable.")
            if isinstance(arg, str):
                arg = (arg,)
            if not (isinstance(func, BaseFilter) or self.getAttributeList() >= set(arg)):
                raise ValueError(
                    "Unsupported attribute " +
                    repr(set(arg) - self.getAttributeList())
                )

    def __call__(self, o) -> bool:
        oper = and_ if self.mode == "and" else or_
        shortcut = oper(True, False)
        ret = not shortcut
        for arg, func in self.filter:
            if isinstance(func, BaseFilter):
                ret = oper(ret, func(o))
            else:
                if isinstance(arg, str):
                    arg = (arg,)
                ret = oper(ret, func(*(getattr(o, attr, False)
                                       for attr in arg)))
            if ret == shortcut:
                break
        return ret

    def apply(self, auctions: Iterable) -> Iterable:
        iterType = type(auctions)
        return iterType(filter(self, auctions))

    def merge(self, o, mode: str = 'and'):
        return BaseFilter((None, self), (None, o), mode=mode)
