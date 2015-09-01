# -*- coding: utf-8 -*-

import logging
import yaml
import jinja2

import admiral.exception as exc

# Try LibYAML first and if unavailable, fall back to pure Python implementation
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

LOG = logging.getLogger(__name__)


def _load_config(config_file):
    try:
        with open(config_file) as fh:
            config = yaml.safe_load(fh)
    except yaml.YAMLError as e:
        msg = "Failed to parse config file {0}: {1}"
        raise exc.UserInputException(msg.format(config_file, str(e)))

    return config


def _validate_config(config):
    # TODO - write config validation using i.e. cerberus library:
    # http://docs.python-cerberus.org/en/latest/
    pass


def _apply_envvars(config, env):
    LOG.debug("Pre-templated config: {0}".format(config))
    tmp = yaml.dump(config, Dumper=Dumper, default_flow_style=False)
    try:
        template = jinja2.Template(tmp)
        rendered_template = template.render(config["environments"][env])
        res = yaml.load(rendered_template, Loader=Loader)
    except (yaml.YAMLError, jinja2.TemplateError) as e:
        msg = "Syntax errors found while templating variables: {0}"
        raise exc.UserInputException(msg.format(str(e)))
    LOG.info("Templated pods configuration: {0}".format(res))
    return res


def load_config(config_file, environment):
    config = _load_config(config_file)
    _validate_config(config)
    config = _apply_envvars(config, environment)
    return config
