import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Optional, TypeVar, cast

from typing_extensions import override

logger = logging.getLogger('sudare')


T = TypeVar('T')


class Data(Generic[T]):
    _value: T

    def __init__(self, value: T, name: str = 'IN') -> None:
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
    @abstractmethod
    def __call__(self, arg: Data[IN], log: bool) -> Data[OUT]: ...

    @abstractmethod
    def __add__(self, right: 'Node[OUT, RET]') -> 'Node[IN, RET]': ...

    @abstractmethod
    def __rshift__(self, right: 'Node[OUT, RET]') -> 'Node[IN, RET]': ...


class Work(Node[IN, OUT]):
    _name: str
    func: Optional[Callable[[IN], OUT]]

    def __init__(self, name: str, func: Optional[Callable[[IN], OUT]] = None):
        self._name = name
        self.func = func

    def register(self, func: Callable[[IN], OUT]) -> None:
        self.func = func

    @property
    def name(self):
        return f'[Work/{self._name}]'

    @name.setter
    def name(self, value):
        self._name = value

    @override
    def __call__(self, arg: IN | Data[IN], log: bool = True) -> Data[OUT]:
        try:
            if log:
                logger.info(f'{self.name} Start')
            if self.func is None:
                raise NotImplementedError(f'[Work/{self.name}] Function is not assigned')
            res: Optional[OUT] = None
            if isinstance(arg, Data):
                res = self.func(arg.output)
            else:
                res = self.func(arg)
            if log:
                logger.info(f'{self.name} Done')
        except Exception as e:
            if log:
                logger.exception(f'{self.name} Work failed, terminated')
            raise e
        return Data(res, name=f'{self.name} Output')

    @override
    def __add__(self, right) -> 'Work[IN, RET]':
        if isinstance(right, Work):

            def work(arg: IN) -> RET:
                lres: Data[OUT] = self(arg, log=False)
                rres: Data[RET] = right(lres, log=False)
                return rres.output

            return Work('+'.join([self._name, right._name]), work)
        else:
            raise NotImplemented  # noqa: F901

    @override
    def __rshift__(self, right: Node[OUT, RET]) -> 'Flow[IN, RET]':
        if isinstance(right, Work):
            return Flow('->'.join([self._name, right._name]), self, right)
        elif isinstance(right, Flow):
            graph = [self, *right.graph]
            return Flow('->'.join([self._name, right._name]), *graph)
        else:
            raise NotImplemented  # noqa: F901


class Flow(Node[IN, OUT]):
    graph: list[Node[Any, Any]]

    def __init__(self, name: str, *node: Node[Any, Any]):
        self._name = name
        self.graph = list(node)

    @property
    def name(self):
        return f'[Flow/{self._name}]'

    @name.setter
    def name(self, value):
        self._name = value

    @override
    def __call__(self, arg: IN | Data[IN], log: bool = True) -> Data[OUT]:
        try:
            logger.info(f'{self.name} Started')
            res: Data[Any] = arg if isinstance(arg, Data) else Data(arg)
            for work in self.graph:
                res = work(res, log=log)
            logger.info(f'{self.name} Done')
        except Exception as e:
            logger.error(f'{self.name} Terminated')
            raise e
        return Data(cast(OUT, res.output), name=f'{self.name}: output')

    @override
    def __add__(self, right) -> 'Flow[IN, RET]':
        if type(right) is Flow:
            graph = [*self.graph, *right.graph]
            return Flow('+'.join([self._name, right._name]), *graph)
        else:
            raise NotImplemented  # noqa: F901

    @override
    def __rshift__(self, right: Node[OUT, RET]) -> 'Flow[IN, RET]':
        if isinstance(right, Work):
            graph = [*self.graph, right]
            return Flow('->'.join([self._name, right._name]), *graph)
        elif isinstance(right, Flow):
            graph = [self, right]
            return Flow('->'.join([self._name, right._name]), *graph)
        else:
            raise NotImplemented  # noqa: F901
