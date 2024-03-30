import logging

from sudareph.core import Data, Flow, Work
from sudareph.flow import Parallel
from sudareph.utils import work_cls, work_fn

__all__ = ['Data', 'Work', 'Flow', 'Parallel', 'work_fn', 'work_cls']
__version__ = '0.0.1'

logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.basicConfig(level=logging.DEBUG, format='{asctime} | {levelname:.4} | {name}: {message}', style='{')
