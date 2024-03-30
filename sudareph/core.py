import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Optional, TypeVar, cast

from typing_extensions import override

logger = logging.getLogger('sudare')


T = TypeVar('T')


class Data(Generic[T]):
    _value: T

    def __init__(self, name: str, value: T) -> None:
        self.name = name
        self._value = value

    @property
    def output(self) -> T:
        return self._value

    def __gt__(self, right: 'Flow[T, OUT]') -> 'Data[OUT]':
        res = self.output
        return right(res)


IN = TypeVar('IN')
OUT = TypeVar('OUT')
RET = TypeVar('RET')


class Node(ABC, Generic[IN, OUT]):
    name: str

    @abstractmethod
    def __call__(self, arg: Data[IN], log: bool) -> Data[OUT]: ...

    @abstractmethod
    def __add__(self, right: 'Node[OUT, RET]') -> 'Node[IN, RET]': ...

    @abstractmethod
    def __rshift__(self, right: 'Node[OUT, RET]') -> 'Node[IN, RET]': ...


class Work(Node[IN, OUT]):
    name: str
    func: Optional[Callable[[IN], OUT]]

    def __init__(self, name: str, func: Optional[Callable[[IN], OUT]]):
        self.name = name
        self.func = func

    @override
    def __call__(self, arg: IN | Data[IN], log: bool = False) -> Data[OUT]:
        try:
            if log:
                logger.info(f'[Work/{self.name}] Start')
            if self.func is None:
                raise NotImplementedError('Function is not assigned')
            res: Optional[OUT] = None
            if isinstance(arg, Data):
                res = self.func(arg.output)
            else:
                res = self.func(arg)
            if log:
                logger.info(f'[Work/{self.name}] Done')
        except Exception as e:
            if log:
                logger.exception(f'Work@{self.name} Work failed, terminated')
            raise e
        return Data(f'[Work/{self.name}] Output', res)

    @override
    def __add__(self, right) -> 'Work[IN, RET]':
        if isinstance(right, Work):

            def work(arg: IN) -> RET:
                lres: Data[OUT] = self(arg, log=False)
                rres: Data[RET] = right(lres, log=False)
                return rres.output

            return Work(f'[Work/{"+".join([self.name, right.name])}]', work)
        else:
            raise NotImplemented  # noqa: F901

    @override
    def __rshift__(self, right: Node[OUT, RET]) -> 'Flow[IN, RET]':
        if isinstance(right, Work):
            return Flow(f'[Work/{"->".join([self.name, right.name])}]', self, right)
        elif isinstance(right, Flow):
            graph = [self, *right.graph]
            return Flow('Compound', *graph)
        else:
            raise NotImplemented  # noqa: F901


class Flow(Node[IN, OUT]):
    graph: list[Node[Any, Any]]

    def __init__(self, name: str, *node: Node[Any, Any]):
        self.name = name
        self.graph = list(node)

    @override
    def __call__(self, arg: IN | Data[IN], log: bool = False) -> Data[OUT]:
        try:
            logger.info(f'[Flow/{self.name}] Started')
            res: Data[Any] = arg if isinstance(arg, Data) else Data('In', arg)
            for work in self.graph:
                res = work(res, log=log)
            logger.info(f'[Flow/{self.name}] Done')
        except Exception as e:
            logger.exception(f'[Flow/{self.name}] Terminated')
            raise e
        return Data(f'{self.name}: output', cast(OUT, res.output))

    @override
    def __add__(self, right) -> 'Flow[IN, RET]':
        if type(right) is Flow:
            graph = [*self.graph, *right.graph]
            return Flow('Compound', *graph)
        else:
            raise NotImplemented  # noqa: F901

    @override
    def __rshift__(self, right: Node[OUT, RET]) -> 'Flow[IN, RET]':
        if isinstance(right, Work):
            graph = [*self.graph, right]
            return Flow('Compound', *graph)
        elif isinstance(right, Flow):
            graph = [self, right]
            return Flow('Compound', *graph)
        else:
            raise NotImplemented  # noqa: F901
