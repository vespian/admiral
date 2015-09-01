# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import logging.handlers as lh
import yaml

import admiral.exception as exception


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


def _load_config(config_file):
    try:
        with open(config_file) as fh:
            config = yaml.safe_load(fh)
    except yaml.YAMLError as e:
        msg = "Failed to parse config file {0}: {1}"
        raise exception.UserInputException(msg.format(config_file, str(e)))

    return config


def _validate_config(config):
    # TODO - write config validation using i.e. cerberus library
    pass


def _apply_envvars(config):
    # TODO - write configuration tempating using env vars
    # return the same configuration for now
    return config


def load_config(config_file):
    config = _load_config(config_file)
    config = _apply_envvars(config_file)
    _validate_config(config)
    return config
