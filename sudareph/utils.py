from functools import wraps
from typing import Any, Callable, TypeVar

from sudareph.core import Flow, Work

IN = TypeVar('IN')
OUT = TypeVar('OUT')


class work_fn:
    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, func: Callable[[IN], OUT]) -> Flow[IN, OUT]:
        return Flow(self.name, Work(self.name, func))


class work_cls:
    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, func: Callable[..., Callable[[IN], OUT]]) -> Callable[..., Flow[IN, OUT]]:
        @wraps(func)
        def init(*args: Any, **kwargs: Any):
            ret = func(*args, **kwargs)
            return Flow(self.name, Work(self.name, ret))

        return init
