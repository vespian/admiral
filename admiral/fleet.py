# -*- coding: utf-8 -*-

import jinja2
import logging
from googleapiclient.errors import HttpError

import fleet.v1 as fleet

import admiral.exception as exc

LOG = logging.getLogger(__name__)


class Fleet():
    _UNIT_TEMPLATE = """
[Unit]
Description=Unit created by Admiral tool for container {{ container_name }}
{% if binds_to %}
BindsTo={{ '.service '.join(binds_to) }}.service
{% endif -%}
After=docker.service
Requires=docker.service

[Service]
TimeoutStartSec=0
ExecStartPre=-/usr/bin/docker kill {{ container_name }}
ExecStartPre=-/usr/bin/docker rm {{ container_name }}
ExecStartPre=/usr/bin/docker pull {{ container_image }}
ExecStart=/usr/bin/docker run {{ container_links }} {{ container_ports }} --name {{ container_name }} {{ container_image }} {{ container_cmd }}
ExecStop=/usr/bin/docker stop {{ container_name }}
{% if machine_of %}

[X-Fleet]
MachineOf={{ machine_of }}.service
{% endif %}
"""

    def _generate_unit_file(self, name, data):
        cp = ' '.join(['--publish ' + port for port in data.get('external_ports', [])])
        cl = ' '.join(['--link ' + link for link in data.get('links', [])])
        template_data = {"container_name": name,
                         "container_image": data['image'],
                         "container_ports": cp,
                         "container_links": cl,
                         "container_cmd": data.get('cmd', ''),
                         "binds_to": data.get('binds_to', []),
                         "machine_of": data.get('machine_of', None),
                         }

        template = jinja2.Template(self._UNIT_TEMPLATE)
        unit_text = template.render(template_data)
        LOG.debug("Generated unit for container {0}: {1}".format(name, unit_text))
        return unit_text

    def __init__(self, fleet_ip, fleet_port):
        conn_string = 'http://{ip}:{port}'.format(ip=fleet_ip, port=fleet_port)
        LOG.debug("Connecting to fleet instance at {0}".format(conn_string))
        try:
            fleet_client = fleet.Client(conn_string)
        except ValueError as e:
            msg = 'Unable to discover fleet: {0}'.format(e)
            raise exc.CommandExecutionError(msg)
        LOG.debug("Connected to {0}".format(conn_string))
        self.conn = fleet_client

    def add(self, pods_configuration):
        for pod in pods_configuration:
            LOG.debug("Adding pod {0} to the cluster".format(pod))
            for container in pods_configuration[pod]['containers']:
                unit_str = self._generate_unit_file(name=container,
                                                    data=pods_configuration[pod]['containers'][container])
                unit = fleet.Unit(from_string=unit_str)
                try:
                    unit = self.conn.create_unit(container + '.service', unit)
                except fleet.APIError as e:
                    msg = 'Unable to create unit for container {0}: {1}'.format(container, e)
                    raise exc.CommandExecutionError(msg)

    def set_state(self, pods_configuration, state):
        for pod in pods_configuration:
            msg = "Setting state for pod {0} to {1}".format(pod, state)
            LOG.info(msg)
            for container in pods_configuration[pod]['containers']:
                msg = "Setting state for container {0} to {1}".format(container,
                                                                      state)
                LOG.debug(msg)
                try:
                        self.conn.set_unit_desired_state(container + ".service", state)
                except fleet.APIError as exc:
                    msg = 'Unable to change unit state: {0}'.format(exc)
                    raise exc.CommandExecutionError(msg)

    def list(self, pods_configuration):
        try:
            for unit_state in self.conn.list_unit_states():
                msg = "{0}: load-state: {1}, current-state:{2}"
                print(msg.format(unit_state['name'],
                                 unit_state['systemdLoadState'],
                                 unit_state['systemdActiveState'],
                                 ))
        except fleet.APIError as exc:
            msg = 'Unable to list unit state: {0}'.format(exc)
            raise exc.CommandExecutionError(msg)

    def delete(self, pods_configuration):
        for pod in pods_configuration:
            LOG.warn("Removing pod {0} from the cluster".format(pod))
            for container in pods_configuration[pod]['containers']:
                LOG.info("Removing container {0}".format(container))
                try:
                    self.conn.destroy_unit(container + ".service")
                except HttpError as exc:
                    # FIXME - fleet library I am using has a problem with
                    # decoding JSON, instead of proper exception you get:
                    # TypeError: the JSON object must be str, not 'bytes'
                    # After fixing it, we should check the reason of the exception
                    # and if it's 404 - ignore it(container does not exists
                    # already).
                    pass
                except fleet.APIError as exc:
                    msg = 'Unable to list unit state: {0}'.format(exc)
                    raise exc.CommandExecutionError(msg)
