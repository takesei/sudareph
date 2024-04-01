from sudareph.data import Data
from sudareph.work import Work


def test_work_definition():
    Summation = Work('Sum')
    work = Summation

    @Summation.register
    def sum(a):
        return 'POST:' + a

    assert isinstance(work, Work)

    res1 = work('ASDF')
    assert isinstance(res1, Data)
    res1 = res1.output
    assert res1 == 'POST:ASDF'

    res2 = work(Data('ASDF'))
    assert isinstance(res2, Data)
    assert res1 == res2.output

    # res3 = 'ASDF' > work
    # assert isinstance(res2, Data)
    # assert res1 == res3.output

    res4 = Data('ASDF') > work
    assert isinstance(res2, Data)
    assert res1 == res4.output


def test_param_work_definition():
    Summation = Work('Sum', prefix=str)
    work = Summation.set(prefix='POST:')

    @Summation.register
    def sum(a, prefix: str):
        return prefix + a

    assert isinstance(work, Work)

    res1 = work('ASDF')
    assert isinstance(res1, Data)
    res1 = res1.output
    assert res1 == 'POST:ASDF'

    res2 = work(Data('ASDF'))
    assert isinstance(res2, Data)
    assert res1 == res2.output

    # res3 = 'ASDF' > work
    # assert isinstance(res2, Data)
    # assert res1 == res3.output

    res4 = Data('ASDF') > work
    assert isinstance(res2, Data)
    assert res1 == res4.output


def test_concat_work():
    Summation = Work('Sum', prefix=str)
    work = Summation.set(prefix='POST:')

    @Summation.register
    def sum(a, prefix: str):
        return prefix + a

    # Work->Work
    flow = work >> work

    # Work->Flow
    work >> flow
