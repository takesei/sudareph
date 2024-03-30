import logging
from typing import Any, TypeVar

from typing_extensions import override

from sudareph.core import Data, Flow, Node, Work

logger = logging.getLogger('sudare')

IN = TypeVar('IN')
OUT = TypeVar('OUT')


class Parallel(Flow[IN, dict[str, Any]]):
    br_graph: dict[str, Node[IN, Any]]

    def __init__(self, name: str, **branch_nodes: Node[IN, Any]):
        self.name = name
        self.br_graph = branch_nodes

    @override
    def __call__(self, arg: IN | Data[IN], log: bool = False) -> Data[dict[str, Any]]:
        try:
            data_arg: Data[Any] = arg if isinstance(arg, Data) else Data(arg)
            logger.info(f'[ParallelFlow/{self.name}] Started')
            res = {k: v(data_arg, log=log).output for k, v in self.br_graph.items()}
            logger.info(f'[ParallelFlow/{self.name}] Done')
        except Exception as e:
            logger.error(f'[ParallelFlow/{self.name}] Terminated')
            raise e
        return Data(res, name=f'{self.name}: output')

    @override
    def __add__(self, right):
        if type(right) is Parallel:
            br_graph = self.br_graph
            for k, v in right.br_graph.items():
                if k in br_graph:
                    br_graph[k] = br_graph[k] >> v
                else:
                    br_graph[k] = v
            return Parallel('Compound', **br_graph)
        else:
            raise NotImplemented  # noqa: F901

    @override
    def __rshift__(self, right: Node[dict[str, Any], OUT]) -> 'Flow[IN, OUT]':
        if isinstance(right, (Work, Flow)):
            graph: list[Parallel[IN] | Node[dict[str, Any], OUT]] = [self, right]
            return Flow('Compound', *graph)
        else:
            raise NotImplemented  # noqa: F901
