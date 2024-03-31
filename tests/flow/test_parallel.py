from sudareph.data import Data
from sudareph.flow import Flow, Parallel
from sudareph.work import Work


def test_parallel_flow():
    Summation = Work('Sum', prefix=str)
    flow = Summation('PRE:') >> Summation('POST:')

    assert isinstance(flow, Flow)

    @Summation.register
    def sum(a, prefix: str):
        return prefix + a

    pipeline = Summation('Init:') >> Parallel(
        'Parallel',
        A=Summation('A1:') >> Summation('A2:'),
        B=Summation('B1:') >> Summation('B2:'),
    )

    res = Data('ARG') > pipeline

    assert res.output == dict(A='A2:A1:Init:ARG', B='B2:B1:Init:ARG')
