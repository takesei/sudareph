import logging
import time
from typing import Callable, Generic, Optional, TypeVar, cast

from sudareph.core import BaseData, BaseFlow, BaseWork, Node
from sudareph.data import Data
from sudareph.flow import Flow

logger = logging.getLogger(__name__)

IN = TypeVar('IN')
OUT = TypeVar('OUT')
RET = TypeVar('RET')


class Work(Generic[IN, OUT]):
    name: str
    func: Optional[Callable[[IN], OUT]]

    def __init__(self, name: str, func: Optional[Callable[[IN], OUT]] = None):
        self._name = name
        self.func = func

    def register(self, func: Callable[[IN], OUT]) -> None:
        self.func = func

    @property
    def fname(self):
        return f'[Work/{self.name}]'

    def __call__(self, arg: IN | BaseData[IN], log: bool = True) -> BaseData[OUT]:
        try:
            if log:
                logger.info(f'{self.fname} Start')
            if self.func is None:
                raise NotImplementedError(f'{self.fname} Function is not assigned')
            if isinstance(arg, BaseData):
                arg = arg.output
            stime = time.time()
            res: OUT = self.func(arg)
            etime = time.time()
            exc_time = etime - stime
            if log:
                logger.info(f'{self.fname} Done ({exc_time:.3f}sec)')
        except Exception as e:
            if log:
                logger.exception(f'{self.fname} Work failed, terminated')
            raise e
        return Data(res, name=f'{self.fname} Output')

    def __rshift__(self, right: Node[OUT, RET]) -> BaseFlow[IN, RET]:
        if isinstance(right, BaseWork):
            return cast(Flow[IN, RET], Flow('->'.join([self.name, right.name]), self, right))
        elif isinstance(right, BaseFlow):
            graph = [self, *right.graph['Main']]
            return cast(Flow[IN, RET], Flow('->'.join([self.name, right.name]), *graph))
        else:
            raise NotImplemented  # noqa: F901
