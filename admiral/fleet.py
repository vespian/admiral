# -*- coding: utf-8 -*-

import jinja2
import logging

import fleet.v1 as fleet

import admiral.exception as exc

LOG = logging.getLogger(__name__)

UNIT_TEMPLATE="""
[Unit]
Description=Unit created by Admiral tool
After=docker.service
Requires=docker.service

[Service]
TimeoutStartSec=0
ExecStartPre=-/usr/bin/docker kill {{ container_name }}
ExecStartPre=-/usr/bin/docker rm {{ container_name }}
ExecStartPre=/usr/bin/docker pull {{ container_image }}
ExecStart=/usr/bin/docker run {{ " " + container_links | default("") }}{{ " " + container_ports | default("") }} --name {{ container_name }} {{ image_name}}{{ " " + container_cmd | default("")}}
ExecStop=/usr/bin/docker stop {{ container_name }}
{% if all_together or all_or_none %}

{% endif %}
"""


class Fleet():
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
            for 

    def start(self, pods_configuration):
        LOG.debug("Starting pods: {0}".format(pods_configuration))
        p.pprint(pods_configuration)

    def stop(self, pods_configuration):
        NotImplementedError("FIXME - stopping pods is not implemented yet")

    def list(self, pods_configuration):
        NotImplementedError("FIXME - listing pods is not implemented yet")

    def delete(self, pods_configuration):
        NotImplementedError("FIXME - deleting pods is not implemented yet")
