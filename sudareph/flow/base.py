import logging
from typing import Any, Callable, Generic, TypeVar, cast

from sudareph.core import BaseData, BaseFlow, BaseWork, Node
from sudareph.data import Data

logger = logging.getLogger(__name__)
IN = TypeVar('IN')
OUT = TypeVar('OUT')
RET = TypeVar('RET')


class Flow(Generic[IN, OUT]):
    name: str
    graph: dict[str, list[Node[Any, Any]]]

    def __init__(self, name: str, *node: Node[Any, Any]):
        self.name = name
        self.graph = {'Main': list(node)}

    def register(self, func: Callable[[], list[Node[Any, Any]]]):
        self.graph |= {'Main': func()}

    @property
    def fname(self):
        return f'[Flow/{self.name}]'

    def __call__(self, arg: IN | BaseData[IN], log: bool = True) -> BaseData[OUT]:
        try:
            logger.info(f'{self.fname} Started')
            res: BaseData[Any] = arg if isinstance(arg, BaseData) else Data(arg)
            for work in self.graph['Main']:
                res = work(res, log=log)
            logger.info(f'{self.fname} Done')
        except Exception as e:
            logger.error(f'{self.fname} Terminated')
            raise e
        return Data(cast(OUT, res.output), name=f'{self.name}: output')

    def __rshift__(self, right: Node[OUT, RET]) -> BaseFlow[IN, RET]:
        if isinstance(right, BaseWork):
            graph = [*self.graph['Main'], right]
            return cast(Flow[IN, RET], Flow('->'.join([self.name, right.name]), *graph))
        elif isinstance(right, BaseFlow):
            graph = [*self.graph['Main'], *right.graph['Main']]
            return cast(Flow[IN, RET], Flow('->'.join([self.name, right.name]), *graph))
        else:
            raise NotImplemented  # noqa: F901
