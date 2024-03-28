from sudareph import Data, Flow, Parallel, work_cls, work_fn


def test_class_decorator():
    @work_cls('Sum')
    class Summation:
        def __init__(self, prefix: str):
            self.prefix = prefix

        def __call__(self, str1: str) -> str:
            return self.prefix + str1

    work = Summation('POST:')
    assert isinstance(work, Flow)

    res = work('ASDF')
    assert isinstance(res, Data)
    assert res.output == 'POST:ASDF'


def test_fn_decorator():
    @work_fn('sum')
    def sum(a):
        return 'POST:' + a

    work = sum
    assert isinstance(work, Flow)

    res = work('ASDF')
    assert isinstance(res, Data)
    assert res.output == 'POST:ASDF'


def test_single_flow():
    @work_cls('Sum')
    class Summation:
        def __init__(self, prefix: str):
            self.prefix = prefix

        def __call__(self, str1: str) -> str:
            return self.prefix + str1

    work = Summation('POST:')
    input = Data('name', 'value')

    result = input > work

    assert result.output == 'POST:value'


def test_multi_flow():
    @work_cls('Sum')
    class Summation:
        def __init__(self, prefix: str):
            self.prefix = prefix

        def __call__(self, str1: str) -> str:
            return self.prefix + str1

    pipeline = Summation('PRE:') >> Summation('POST:')
    res = Data('name', 'value') > pipeline

    assert res.output == 'POST:PRE:value'


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
