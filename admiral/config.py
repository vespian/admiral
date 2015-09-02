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


def _normalize_container_names(config, env):
    for pod in config['pods']:
        new_h = {}
        h = config['pods'][pod]['containers']
        for old_name in h:
            new_name_f = env + "_" + pod + "_{0}"
            # Fix links:
            if 'links' in h[old_name]:
                new_links = []
                old_links = h[old_name]['links']
                for link in old_links:
                    c, alias = link.split(':')
                    new_links.append(new_name_f.format(c) + ':' + alias)
                h[old_name]['links'] = new_links

            # Fix machine_of:
            if 'machine_of' in h[old_name]:
                h[old_name]['machine_of'] = new_name_f.format(h[old_name]['machine_of'])

            # Fix binds_to:
            if 'binds_to' in h[old_name]:
                h[old_name]['binds_to'] = [new_name_f.format(unit) for unit in h[old_name]['binds_to']]

            # Replace the hash:
            new_h[new_name_f.format(old_name)] = h[old_name]
        config['pods'][pod]['containers'] = new_h


def load_config(config_file, environment):
    config = _load_config(config_file)
    _validate_config(config)
    config = _apply_envvars(config, environment)
    _normalize_container_names(config, environment)
    return config
