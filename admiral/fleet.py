# -*- coding: utf-8 -*-

import jinja2
import logging

import fleet.v1 as fleet

import admiral.exception as exc

LOG = logging.getLogger(__name__)


class Fleet():
    _UNIT_TEMPLATE = """
[Unit]
Description=Unit created by Admiral tool for container {{ container_name }}
{% if all_or_none and pod_containers %}
BindsTo={{ ' '.join(pod_containers) }}
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
{% if all_together and pod_containers %}

[X-Fleet]
MachineOf={{ pod_containers[0] }}
{% endif %}
"""

    def _generate_unit_file(self, name, data, pod_containers, all_or_none, all_together):
        cp = ' '.join(['--publish ' + port for port in data.get('external_ports', [])])
        cl = ' '.join(['--link ' + link for link in data.get('links', [])])
        template_data = {"container_name": name,
                         "all_or_none": all_or_none,
                         "all_together": all_together,
                         "pod_containers": [x for x in pod_containers if x != name],
                         "container_image": data['image'],
                         "container_ports": cp,
                         "container_links": cl,
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
            pod_containers = pods_configuration[pod]['containers'].keys()
            for container in pods_configuration[pod]['containers']:
                unit_str = self._generate_unit_file(name=container,
                                                    data=pods_configuration[pod]['containers'][container],
                                                    pod_containers=pod_containers,
                                                    all_or_none=pods_configuration[pod]['all_or_none'],
                                                    all_together=pods_configuration[pod]['all_together'])

                unit = fleet.Unit(from_string=unit_str)
                try:
                    unit = fleet_client.create_unit(container, unit)
                except fleet.APIError as e:
                    msg = 'Unable to create unit for container {0}: {1}'.format(container, e)
                    raise exc.CommandExecutionError(msg)

    def start(self, pods_configuration):
        LOG.debug("Starting pods: {0}".format(pods_configuration))

    def stop(self, pods_configuration):
        NotImplementedError("FIXME - stopping pods is not implemented yet")

    def list(self, pods_configuration):
        NotImplementedError("FIXME - listing pods is not implemented yet")

    def delete(self, pods_configuration):
        NotImplementedError("FIXME - deleting pods is not implemented yet")
