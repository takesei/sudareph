import logging
from typing import Any, Callable, Generic, TypeVar, cast

from typing_extensions import TypeVarTuple

from sudareph.core import BaseData, BaseFlow, BaseMultiFlow, BaseWork, Node
from sudareph.data import Data

logger = logging.getLogger(__name__)
IN = TypeVar('IN')
OUT = TypeVar('OUT')
RET = TypeVar('RET')

Ts = TypeVarTuple('Ts')


class Flow(Generic[IN, OUT]):
    name: str
    graph: list[Node[Any, Any]]

    def __init__(self, name: str, *node: Node[Any, Any]):
        self.name = name
        self.graph = list(node)

    def register(self, func: Callable[[], Node[Any, Any]]):
        res = func()
        if isinstance(res, BaseWork):
            self.graph = [res]
        elif isinstance(res, BaseFlow):
            self.graph = res.graph
        elif isinstance(res, BaseMultiFlow):
            raise TypeError('Use Parallel flow instead')

    @property
    def fname(self):
        return f'[Flow/{self.name}]'

    def __call__(self, arg: IN | BaseData[IN], log: bool = True) -> BaseData[OUT]:
        try:
            logger.info(f'{self.fname} Started')
            res: BaseData[Any] = arg if isinstance(arg, BaseData) else Data(arg)
            for work in self.graph:
                res = work(res, log=log)
            logger.info(f'{self.fname} Done')
        except Exception as e:
            logger.error(f'{self.fname} Terminated')
            logger.error(f'{work} <- [{self.graph}]')
            raise e
        return Data(cast(OUT, res.output), name=f'{self.name}: output')

    def __rshift__(self, right: Node[OUT, RET]) -> BaseFlow[IN, RET]:
        if isinstance(right, BaseWork):
            graph = [*self.graph, right]
            return cast(Flow[IN, RET], Flow('->'.join([self.name, right.name]), *graph))
        elif isinstance(right, BaseMultiFlow):
            graph = [self, right]
            return cast(Flow[IN, RET], Flow('->'.join([self.name, right.name]), *graph))
        elif isinstance(right, BaseFlow):
            graph = [*self.graph, *right.graph]
            return cast(Flow[IN, RET], Flow('->'.join([self.name, right.name]), *graph))
        else:
            raise NotImplemented  # noqa: F901
