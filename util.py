# -*- coding: utf-8 -*-
import logging
import os
import types


logger = logging.getLogger(__name__)


def config_from_pyfile(filename, suppress=False):
    if os.path.isfile(filename):
        filename = os.path.abspath(filename)
    else:
        if suppress is False:
            raise RuntimeError('cannot find config file: "%s"' % filename)
        else:
            return {}

    logger.info('loading config from "%s"' % filename)
    d = types.ModuleType('config')
    d.__file__ = filename

    with open(filename) as f:
        exec(compile(f.read(), filename, 'exec'), d.__dict__)

    rv = {}
    for i in dir(d):
        if i == i.upper():
            rv[i] = getattr(d, i)
    return rv
