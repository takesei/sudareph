import pytest

from sudareph.core import BaseData, BaseFlow, BaseWork, Node
from sudareph.data import Data
from sudareph.flow import Flow
from sudareph.work import Work


def test_match_flow():
    flow = [Flow('temp')]

    for f in flow:
        assert isinstance(f, BaseFlow), f'failed at {f}'
        assert isinstance(f, Node), f'failed at {f}'


def test_match_work():
    cb_works = [Work('temp', hoge=str)]
    for w in cb_works:
        assert isinstance(w, Work)
        with pytest.raises(AttributeError):
            w.set()
            w.set(asdf='nanachi')
            w.set(hoge='fuga', asdf='nanachi')
        w.set(hoge='fuga')

    works = [Work('temp'), *[c.set(hoge='fuga') for c in cb_works]]

    for w in works:
        assert isinstance(w, BaseWork), f'failed at {w}'
        assert isinstance(w, Node), f'failed at {w}'


def test_match_data():
    data = [Data('temp')]

    for d in data:
        assert isinstance(d, BaseData), f'failed at {d}'
