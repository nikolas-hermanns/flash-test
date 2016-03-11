'''
Created on Jan 16, 2016

@author: enikher
'''
import logging
import datetime

LOG = logging.getLogger(__name__)
LOG_LEVEL = logging.DEBUG
LOG_PATH = "./dlService.log"
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    filename=LOG_PATH,
                    datefmt='%Y-%m-%dT:%H:%M:%s', level=LOG_LEVEL)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
console.setFormatter(formatter)
LOG.addHandler(console)


def log_enter_exit(func):

    def inner(self, *args, **kwargs):
        LOG.debug(("Entering %(cls)s.%(method)s "
                   "args: %(args)s, kwargs: %(kwargs)s") %
                  {'cls': self.__class__.__name__,
                   'method': func.__name__,
                   'args': args,
                   'kwargs': kwargs})
        start = datetime.datetime.now()
        ret = func(self, *args, **kwargs)
        end = datetime.datetime.now()
        LOG.debug(("Exiting %(cls)s.%(method)s. "
                   "Spent %(duration)s sec. "
                   "Return %(return)s") %
                  {'cls': self.__class__.__name__,
                   'duration': end - start,
                   'method': func.__name__,
                   'return': ret})
        return ret
    return inner
