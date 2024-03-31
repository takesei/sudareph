from sudareph.data import Data
from sudareph.flow import Flow
from sudareph.work import Work


def test_multi_flow():
    Summation = Work('Sum', prefix=str)
    flow = Summation('PRE:') >> Summation('POST:')

    assert isinstance(flow, Flow)

    @Summation.register
    def sum(a, prefix: str):
        return prefix + a

    res1 = flow('value')
    assert not isinstance(res1, Data)
    assert res1 == 'POST:PRE:value'

    res2 = flow(Data('value'))
    assert not isinstance(res2, Data)
    assert res1 == res2.output

    res3 = 'value' > flow
    assert isinstance(res2, Data)
    assert res1 == res3.output

    res4 = Data('value') > flow
    assert isinstance(res2, Data)
    assert res1 == res4.output
