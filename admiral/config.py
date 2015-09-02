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
    """Load configuration

    Args:
        config_file: path to the file that should be read

    Returns:
        Configuration hash - config file after parsing.
    """
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
    """Fill in all template placeholders with environment data

    Some of the variables depend on envrionment. In order to provide
    different setup for different environments, we template the configuration
    and with environment data.

    The substituion is simple - change the configuration hash back to plaintext,
    use jinja to template with the data from environments seciton, and then
    convet it back to hash.

    Args:
        config: configuration hash that should be templated
        env: environent data to use

    Returns:
        Configuration hash destined for particular environment
    """
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
    """Expand container names with pod and environement data

    Container names defined in configuration file do not take into account
    different envrionments where the configuration can be deployed. The purpose
    of this function is to rename all the container names that can be found in
    configuration file so that pod and environemnt is reflected. I.E.

        redis becomes dev_giant-weather_redis (env: dev, pod: giant-weather)

    Places where this renaming is necessary include:
        - `machine_of` field
        - `binds_to` list
        - `links` list
        - container names in each pod hash

    Args:
        config: hash containing the configuration for processing
        env: target environment for the script

    Returns:
        Configuration with all the names fixed
    """
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
    """Load and process the configuration

    This function takes care of all processing neccesary for the config file,
    such as templating, validation, loading, etc...

    Args:
        config_file: location of the config file
        environment: target environment that will be used while reconfiguring
                     the cluster
    Returns:
        Parsed config file
    """
    config = _load_config(config_file)
    _validate_config(config)
    config = _apply_envvars(config, environment)
    _normalize_container_names(config, environment)
    return config
