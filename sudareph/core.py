import logging
from typing import Any, Callable, Protocol, TypeVar, runtime_checkable

from typing_extensions import override

logger = logging.getLogger(__name__)


IN = TypeVar('IN')
OUT = TypeVar('OUT')
RET = TypeVar('RET')


@runtime_checkable
class Node(Protocol[IN, OUT]):
    @property
    def name(self) -> str: ...
    def __call__(self, arg: IN | 'BaseData[IN]', log: bool) -> 'BaseData[OUT]': ...
    def __rshift__(self, right: 'Node[OUT, RET]') -> 'Node[IN, RET]': ...


@runtime_checkable
class BaseWork(Node[IN, OUT], Protocol):
    @property
    def func(self) -> Callable[[IN], OUT]: ...

    @override
    def __rshift__(self, right: 'Node[OUT, RET]') -> 'BaseFlow[IN, RET]': ...


@runtime_checkable
class BaseFlow(Node[IN, OUT], Protocol):
    @property
    def graph(self) -> dict[str, list[Node[Any, Any]]]: ...

    @override
    def __rshift__(self, right: 'Node[OUT, RET]') -> 'BaseFlow[IN, RET]': ...


T = TypeVar('T')


@runtime_checkable
class BaseData(Protocol[T]):
    @property
    def output(self) -> T: ...

    def __gt__(self, right: 'Node[T, RET]') -> 'BaseData[RET]': ...
