from typing import Any

from sudareph.data import Data
from sudareph.flow import Parallel
from sudareph.work import Work


def test_parallel_flow():
    Summation = Work('Sum', prefix=str)
    pipeline = Parallel(
        'Parallel',
        A=Summation.set(prefix='A1:') >> Summation.set(prefix='A2:'),
        B=Summation.set(prefix='B1:') >> Summation.set(prefix='B2:'),
    )

    @Summation.register
    def sum(a, prefix: str):
        return prefix + a

    res = Data('ARG') > pipeline

    assert res.output == dict(A='A2:A1:ARG', B='B2:B1:ARG')


def test_parallel_complicated_flow():
    Summation = Work('Sum', prefix=str)
    Convert = Work('Convert dict to list')
    pipeline = (
        Summation.set(prefix='Init:')
        >> Parallel(
            'Parallel',
            A=Summation.set(prefix='A1:') >> Summation.set(prefix='A2:'),
            B=Parallel(
                'Inner',
                temp=Summation.set(prefix='B1:') >> Summation.set(prefix='B2:'),
            ),
        )
        # >> Convert
    )

    @Summation.register
    def sum(a, prefix: str):
        return prefix + a

    @Convert.register
    def convert(obj: dict[Any, Any]) -> list[Any]:
        return obj.values()

    Data('ARG') > pipeline
