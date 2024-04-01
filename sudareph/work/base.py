import logging
import time
from copy import copy
from typing import Any, Callable, Concatenate, Generic, Optional, ParamSpec, TypeVar, cast

from sudareph.core import BaseData, BaseFlow, BaseMultiFlow, BaseWork, Node
from sudareph.data import Data
from sudareph.flow import Flow

logger = logging.getLogger(__name__)

IN = TypeVar('IN')
OUT = TypeVar('OUT')
RET = TypeVar('RET')
PRM = ParamSpec('PRM')

# Only the class that matches basework


class Functor(Generic[IN, OUT]):
    func: Optional[Callable[[IN], OUT]]

    def __init__(self, func: Optional[Callable[[IN], OUT]]) -> None:
        self.func = func

    def __call__(self, arg: IN, *args: PRM.args, **kwargs: PRM.kwargs) -> OUT:
        if self.func is None:
            raise NotImplementedError('Function is not assigned')
        return self.func(arg, *args, **kwargs)

    def register(self, func: Callable[[IN], OUT]):
        self.func = func


class Work(Generic[IN, OUT]):
    name: str
    func: Functor[IN, OUT]
    kwtype: dict[str, type[Any]]
    kwargs: dict[str, Any]

    def __init__(self, name: str, func: Optional[Callable[Concatenate[IN, PRM], OUT]] = None, **kwtype: type[Any]):
        self.name = name
        self.func = Functor(func)
        self.kwtype = {} | kwtype
        self.kwargs = {}

    def register(self, func: Callable[[IN], OUT]) -> None:
        self.func.register(func)

    def set(self, **kwargs: Any) -> 'Work[IN, OUT]':
        if len(kwargs.keys()) != len(self.kwtype.keys()):
            raise AttributeError(f'Number of keywords must be the same, got {kwargs}, expects {self.kwtype}')
        self.kwargs |= {k: v(kwargs[k]) for k, v in self.kwtype.items()}
        return self.copy()

    def copy(self) -> 'Work[IN, OUT]':
        work: Work[IN, OUT] = Work(self.name, self.func, **copy(self.kwtype))
        work.kwargs = copy(self.kwargs)
        return work

    @property
    def fname(self):
        return f'[Work/{self.name}]'

    def __call__(self, arg: IN | BaseData[IN], log: bool = True, **kwargs: Any) -> BaseData[OUT]:
        try:
            if log:
                logger.info(f'{self.fname} Start')
            if len(self.kwtype.keys()) != len(self.kwargs.keys()):
                raise AttributeError(f'{self.name} Function Parameter is not assigned')
            if isinstance(arg, BaseData):
                arg = arg.output
            stime = time.time()
            res: OUT = self.func(arg, **self.kwargs)
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
        elif isinstance(right, BaseMultiFlow):
            graph: list[Node[Any, Any]] = [Flow(self.name, self), right]
            return cast(Flow[IN, RET], Flow('->'.join([self.name, right.name]), *graph))
        elif isinstance(right, BaseFlow):
            graph = [self, *right.graph]
            return cast(Flow[IN, RET], Flow('->'.join([self.name, right.name]), *graph))
        else:
            raise NotImplemented  # noqa: F901
