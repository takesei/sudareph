import logging
from functools import wraps
from typing import Any, Callable, Generic, TypeVar, cast

logger = logging.getLogger(__name__)


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
R = TypeVar('R')


class Work(Generic[IN, OUT]):
    name: str
    func: Callable[[IN], OUT]

    def __init__(self, name: str, func: Callable[[IN], OUT]):
        self.name = name
        self.func = func

    def __call__(self, arg: IN) -> Data[OUT]:
        logger.info(f'[Work/{self.name}] Started')
        try:
            res = self.func(arg)
        except Exception as e:
            logger.exception(f'Work@{self.name} Work failed')
            raise e
        else:
            logger.info(f'[Work/{self.name}] Done')
            return Data(f'[Work/{self.name}] Output', res)

    def concat(self, *works: 'Work[Any, Any]') -> 'Work[IN, Any]':
        def work(arg: IN) -> Any:
            res: Any = self.func(arg)
            for work in works:
                res = work.func(res)
            return res

        return Work(f'[Work/{"->".join([w.name for w in works])}]', work)


class Flow(Generic[IN, OUT]):
    works: list[Work[Any, Any]]

    def __init__(self, name: str, *works: Work[Any, Any]):
        self.name = name
        self.works = list(works)

    def __call__(self, arg: IN) -> Data[OUT]:
        logger.info(f'[Flow/{self.name}] Started')
        try:
            res: Any = arg
            for work in self.works:
                res = work(res).output
            res = cast(OUT, res)
        except Exception as e:
            logger.exception(f'[Flow/{self.name}] Terminated')
            raise e
        else:
            logger.info(f'[Flow/{self.name}] Done')
            return Data(f'{self.name}: output', res)

    def __rshift__(self, right: 'Flow[OUT, R]') -> 'Flow[IN, R]':
        works = self.works + right.works
        return Flow(f'{self.name}->{right.name}', *works)


class Parallel(Flow[IN, dict[str, Any]]):
    def __init__(
        self,
        name: str,
        **works: Work[IN, Any],
    ):
        self.name = name

        def func(arg: IN) -> dict[str, Any]:
            res: dict[str, Any] = {}
            for k, v in works.items():
                v.name = f'ParallelWork@{k}={v.name}'
                res |= {k: v(arg).output}
            return res

        self.works = [Work(f'<ParallelFlow/{self.name}>', func)]
        self._works = works

    # TODO: Never called
    def __call__(self, arg) -> Data[dict[str, Any]]:
        logger.info(f'[ParallelFlow/{self.name}] Started')
        try:
            res = {k: v(arg).output for k, v in self._works.items()}
        except Exception as e:
            logger.error(f'[ParallelFlow/{self.name}] Terminated')
            raise e
        else:
            logger.info(f'[ParallelFlow/{self.name}] Done')
            return Data(f'{self.name}: output', res)


class work_fn:
    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, func: Callable[[IN], OUT]) -> Flow[IN, OUT]:
        return Flow(self.name, Work(self.name, func))


class work_cls:
    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, func: Callable[..., Callable[[IN], OUT]]) -> Callable[..., Flow[IN, OUT]]:
        @wraps(func)
        def init(*args: Any, **kwargs: Any):
            ret = func(*args, **kwargs)
            return Flow(self.name, Work(self.name, ret))

        return init
