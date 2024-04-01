import logging
from typing import Generic, TypeVar

from sudareph.core import BaseData, Node

logger = logging.getLogger(__name__)
T = TypeVar('T')
RET = TypeVar('RET')


class Data(Generic[T]):
    _value: T

    def __init__(self, value: T, name: str = 'IN') -> None:
        self.name = name
        self._value = value

    @property
    def output(self) -> T:
        return self._value

    def __gt__(self, right: Node[T, RET]) -> BaseData[RET]:
        return right(self, log=False)
