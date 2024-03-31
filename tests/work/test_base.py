from sudareph.data import Data
from sudareph.flow import Flow
from sudareph.work import Work


def test_fn_decorator():
    Summation = Work('Sum')
    work = Summation

    @Summation.register
    def sum(a):
        return 'POST:' + a

    assert isinstance(work, Work)

    res1 = work('ASDF')
    assert not isinstance(res1, Data)
    assert res1 == 'POST:ASDF'

    res2 = work(Data('ASDF'))
    assert not isinstance(res2, Data)
    assert res1 == res2.output

    res3 = 'ASDF' > work
    assert isinstance(res2, Data)
    assert res1 == res3.output

    res4 = Data('ASDF') > work
    assert isinstance(res2, Data)
    assert res1 == res4.output


def test_param_decorator():
    Summation = Work('Sum', prefix=str)
    work = Summation('POST:')

    @Summation.register
    def sum(a, prefix: str):
        return prefix + a

    assert isinstance(work, Flow)

    res1 = work('ASDF')
    assert not isinstance(res1, Data)
    assert res1 == 'POST:ASDF'

    res2 = work(Data('ASDF'))
    assert not isinstance(res2, Data)
    assert res1 == res2.output

    res3 = 'ASDF' > work
    assert isinstance(res2, Data)
    assert res1 == res3.output

    res4 = Data('ASDF') > work
    assert isinstance(res2, Data)
    assert res1 == res4.output


def test_concat_work():
    assert False


def test_concat_flow():
    assert False


# def test_multi_flow():
#     @work_cls('Sum')
#     class Summation:
#         def __init__(self, prefix: str):
#             self.prefix = prefix
#
#         def __call__(self, str1: str) -> str:
#             return self.prefix + str1
#
#     pipeline = Summation('PRE:') >> Summation('POST:')
#     res = Data('value') > pipeline
#
#     assert res.output == 'POST:PRE:value'
