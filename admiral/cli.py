# -*- coding: utf-8 -*-

import click
import logging

import admiral.utils as u


LOG = logging.getLogger(__name__)


class Config(object):
    def __init__(self, env, config):
        self.env = env
        self.config = config


@click.group()
@click.option('-e', '--env', required=True,
              help="Environment to deploy to")
@click.option('-v', '--verbose', count=True,
              help='Increase the verbosity of the script')
@click.option('-s', '--std-err', is_flag=True,
              help='Log to STDERR as well.')
@click.option('-c', '--config', required=True,
              type=click.Path(exists=True, file_okay=True, dir_okay=False,
                              resolve_path=True, readable=True),)
@click.pass_context
def cli(ctx, env, verbose, std_err, config_file_path):

    u.init_logging(verbosity=verbose, std_err=std_err)
    config = u.load_config(config_file_path)

    ctx.obj = Config(env, config)


@click.command()
@click.option('-p', '--pod', multiple=True,
              help="Pod to add/deploy, deploy everything by default")
@click.pass_obj
def add(ctx, pod):
    pass


@click.command()
@click.option('-p', '--pod', multiple=True,
              help="Pod to start, start everything by default")
@click.pass_obj
def start(ctx, pod):
    pass


@click.command()
@click.option('-p', '--pod', multiple=True,
              help="Pod to stop, stop all pods specified by config by default")
@click.pass_obj
def stop(ctx, pod):
    raise NotImplementedError("FIXME - stopping pods is not implemented yet")


@click.command()
@click.option('-p', '--pod', multiple=True,
              help="Pod to list/show, output everything by default")
@click.pass_obj
def list(ctx, pod):
    raise NotImplementedError("FIXME - listing pods is not implemented yet")


@click.command()
@click.option('-p', '--pod', multiple=True,
              help="Pod to delete, delete all pods specified in config"
                   " by default")
@click.pass_obj
def delete(ctx, pod):
    raise NotImplementedError("FIXME - deleting pods is not implemented yet")
