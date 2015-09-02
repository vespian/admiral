# -*- coding: utf-8 -*-

import click
import functools
import logging
import sys
import traceback

import admiral.utils as u
import admiral.exception as exception
import admiral.config as c
import admiral.fleet as f


LOG = logging.getLogger(__name__)


def handle_exceptions(f):
    """Generic exception handling and logging

    This decorator takes care of logging exceptions (if possible) so that they
    could be analyzed later. It also tries to translate some of the well-known
    conditions to more human-friendly form.

    Args:
        f: function to wrap

    Returns:
        Wrapped function
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except exception.UserInputException as e:
            LOG.error("Usage error: {0}".format(e))
        except exception.LocalException as e:
            LOG.exception("Fatal error occured: {0}, terminating!".format(e),
                          exc_info=True)
        except Exception as e:
            msg = 'Uncaught exception raised, terminating!\n'
            sys.stderr.write(msg)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type,
                                               exc_value,
                                               exc_traceback)
            msg = ''.join(line for line in lines)
            sys.stderr.write(msg)
            # Let's try logging it as well:
            LOG.warn(msg)
    return wrapper


@click.group()
@click.option('-e', '--env', required=True,
              help="Environment to deploy to")
@click.option('-v', '--verbose', count=True,
              help='Increase the verbosity of the script')
@click.option('-s', '--std-err', is_flag=True,
              help='Log to STDERR as well.')
@click.option('-c', '--config-file', required=True,
              type=click.Path(exists=True, file_okay=True, dir_okay=False,
                              resolve_path=True, readable=True),)
@handle_exceptions
@click.pass_context
def cli(ctx, env, verbose, std_err, config_file):
    """Main entrypoint for the script.

    The task of this function is to initialize context for subcommands,
    gather and process the data from command line.

    Args:
        env: environment to deploy to
        verbose: integer describing desired level of verbosity
        std_err: should the data be printed to stderr as well
        config_file: location of the config file to read
    """
    # FIXME - not sure how to force click to make subcommands mandatory
    u.init_logging(verbosity=verbose, std_err=std_err)
    config = c.load_config(config_file, env)

    fleet_conn = f.Fleet(fleet_ip=config["fleet_ip"],
                         fleet_port=config["fleet_port"])

    ctx.obj = {"pods": config["pods"],
               "conn": fleet_conn}


@cli.command()
@click.option('-p', '--pod', multiple=True,
              help="Pod to add/deploy, deploy everything by default")
@click.pass_obj
def add(ctx, pod):
    pods_conf = u.trim_hash(ctx["pods"], pod)
    ctx["conn"].add(pods_conf)


@cli.command()
@click.option('-p', '--pod', multiple=True,
              help="Pod to start, start everything by default")
@click.option('-s', '--state', required=True,
              type=click.Choice(['inactive', 'loaded', 'launched']),
              help="State to set.")
@click.pass_obj
def set_state(ctx, pod, state):
    # FIXME
    pods_conf = u.trim_hash(ctx["pods"], pod)
    ctx["conn"].set_state(pods_conf, state)


@cli.command()
@click.option('-p', '--pod', multiple=True,
              help="Pod to list/show, output everything by default")
@click.pass_obj
def list(ctx, pod):
    pods_conf = u.trim_hash(ctx["pods"], pod)
    ctx["conn"].list()


@cli.command()
@click.option('-p', '--pod', multiple=True,
              help="Pod to delete, delete all pods specified in config"
                   " by default")
@click.pass_obj
def delete(ctx, pod):
    pods_conf = u.trim_hash(ctx["pods"], pod)
    ctx["conn"].delete(pods_conf)
