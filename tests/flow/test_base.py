from sudareph.data import Data
from sudareph.flow import Flow
from sudareph.work import Work


def test_single_flow():
    Summation = Work('Sum', prefix=str)
    flow = Summation.set(prefix='PRE:') >> Summation.set(prefix='POST:')

    assert isinstance(flow, Flow)

    @Summation.register
    def sum(a, prefix: str):
        return prefix + a

    res1 = flow('ASDF')
    assert isinstance(res1, Data)
    res1 = res1.output
    assert res1 == 'POST:PRE:ASDF'

    res2 = flow(Data('ASDF'))
    assert isinstance(res2, Data)
    assert res1 == res2.output

    # res3 = 'ASDF' > flow
    # assert isinstance(res2, Data)
    # assert res1 == res3.output

    res4 = Data('ASDF') > flow
    assert isinstance(res2, Data)
    assert res1 == res4.output


def test_flow_assign():
    flow = Flow('Summerize')

    Summation = Work('Sum', prefix=str)

    @flow.register
    def summerize():
        return Summation.set(prefix='PRE:') >> Summation.set(prefix='POST:')

    @Summation.register
    def sum(a, prefix: str):
        return prefix + a

    assert isinstance(flow, Flow)

    res1 = flow('ASDF')
    assert isinstance(res1, Data)
    res1 = res1.output
    assert res1 == 'POST:PRE:ASDF'

    res2 = flow(Data('ASDF'))
    assert isinstance(res2, Data)
    assert res1 == res2.output

    # res3 = 'ASDF' > flow
    # assert isinstance(res2, Data)
    # assert res1 == res3.output

    res4 = Data('ASDF') > flow
    assert isinstance(res2, Data)
    assert res1 == res4.output
