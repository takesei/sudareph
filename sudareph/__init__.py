import logging

from sudareph import data, flow, work
from sudareph.core import BaseData, BaseFlow, BaseWork, Node

__all__ = ['Data', 'work', 'flow', 'Parallel', 'Node', 'BaseFlow', 'BaseWork', 'BaseData', 'data']
__version__ = '0.0.1'

logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.basicConfig(level=logging.DEBUG, format='{asctime} | {levelname:.4} | {name}: {message}', style='{')
