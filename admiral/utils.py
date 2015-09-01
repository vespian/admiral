# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import logging.handlers as lh


def trim_hash(in_hash, hash_keys):
    if hash_keys:
        return {k: in_hash[k] for k in hash_keys}
    else:
        return in_hash


def init_logging(verbosity=0, std_err=False, syslog_facility="LOG_USER"):
    logger = logging.getLogger()

    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)

    if verbosity == 0:
        # Print/log only important stuff:
        logger.setLevel(logging.WARN)
        fmt = logging.Formatter('%(message)s')
    elif verbosity == 1:
        # Print most of the stuff:
        logger.setLevel(logging.INFO)
        fmt = logging.Formatter('%(levelname)s: %(message)s')
    else:
        # Here be dragons:
        logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter('%(filename)s[%(process)d] ' +
                                '%(levelname)s: %(message)s')

    syslog_h = lh.SysLogHandler(address='/dev/log',
                                facility=getattr(lh.SysLogHandler,
                                                 syslog_facility))
    syslog_h.setFormatter(fmt)
    logger.addHandler(syslog_h)

    if std_err:
        stdout_h = logging.StreamHandler()
        stdout_h.setFormatter(fmt)
        logger.addHandler(stdout_h)
