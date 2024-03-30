from sudareph import Data, Parallel, work_cls


def test_parallel_flow():
    @work_cls('Sum')
    class Summation:
        def __init__(self, prefix: str):
            self.prefix = prefix

        def __call__(self, str1: str) -> str:
            return self.prefix + str1

    pipeline = Summation('Init:') >> Parallel(
        'Parallel',
        A=Summation('A1:') >> Summation('A2:'),
        B=Summation('B1:') >> Summation('B2:'),
    )

    res = Data('name', 'ARG') > pipeline

    assert res.output == dict(A='A2:A1:Init:ARG', B='B2:B1:Init:ARG')
