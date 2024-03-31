import logging
from typing import Any, Generic, TypeVar, cast

from sudareph.core import BaseData, BaseFlow, Node
from sudareph.data import Data
from sudareph.flow import Flow
from sudareph.work import Work

logger = logging.getLogger('sudare')

IN = TypeVar('IN')
OUT_co = TypeVar('OUT_co', bound=dict[str, Any], covariant=True)
RET = TypeVar('RET')


class Parallel(Generic[IN, OUT_co]):
    graph: dict[str, list[Node[Any, Any]]]

    def __init__(self, name: str = 'Parallel', **branch_nodes: Node[Any, Any]):
        self.name = name
        self.graph = {}
        for k, v in branch_nodes.items():
            self.graph |= {k: [v]}

    @property
    def fname(self):
        return f'[ParallelFlow/{self.name}]'

    def __call__(self, arg: IN | BaseData[IN], log: bool = False) -> BaseData[OUT_co]:
        try:
            data_arg: Data[Any] = arg if isinstance(arg, Data) else Data(arg)
            logger.info(f'{self.fname} Started')
            res = {k: v[0](data_arg, log=log).output for k, v in self.graph.items()}
            logger.info(f'{self.fname} Done')
        except Exception as e:
            logger.error(f'{self.fname} Terminated')
            raise e
        return Data(cast(OUT_co, res), name=f'{self.name}: output')

    def __rshift__(self, right: Node[OUT_co, RET]) -> BaseFlow[IN, RET]:
        if isinstance(right, (Work, Flow)):
            graph = [self, right]
            return cast(Flow[IN, RET], Flow('Compound', *graph))
        else:
            raise NotImplemented  # noqa: F901
