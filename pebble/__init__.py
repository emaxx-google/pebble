__author__ = 'Matteo Cafasso'
__version__ = '5.0.7'
__license__ = 'LGPL'


__all__ = ['waitforthreads',
           'waitforqueues',
           'synchronized',
           'sighandler',
           'ProcessFuture',
           'MapFuture',
           'ProcessMapFuture',
           'ProcessExpired',
           'ProcessPool',
           'ThreadPool']


from pebble.decorators import synchronized, sighandler
from pebble.functions import waitforqueues, waitforthreads
from pebble.common import ProcessExpired, ProcessFuture, CONSTS
from pebble.pool import ThreadPool, ProcessPool, MapFuture, ProcessMapFuture
