# -*- coding: utf-8 -*-

#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Client side of the conductor RPC API."""

from oslo_config import cfg
import oslo_messaging as messaging

from cyborg.common import constants
from cyborg.common import exception
from cyborg.common import rpc
from cyborg.objects import base as objects_base


CONF = cfg.CONF


def _compute_host(host, deployable):
    '''Get the destination host for a message.

    :param host: explicit host to send the message to.
    :param instance: If an explicit host was not specified, use
                     deployable['host']

    :returns: A host
    '''
    if host:
        return host
    if not deployable:
        raise exception.CyborgException(_('No compute host specified'))
    if not deployable.host:
        raise exception.CyborgException(_('Unable to find host for '
                                          'Deployable %s') % deployable.uuid)
    return deployable.host


class AgentAPI(object):
    """Client side of the Agent RPC API.

    API version history:

    |    1.0 - Initial version.

    """

    RPC_API_VERSION = '1.0'

    def __init__(self, topic=None):
        super(AgentAPI, self).__init__()
        self.topic = topic or constants.AGENT_TOPIC
        target = messaging.Target(topic=self.topic,
                                  version='1.0')
        serializer = objects_base.CyborgObjectSerializer()
        self.client = rpc.get_client(target,
                                     version_cap=self.RPC_API_VERSION,
                                     serializer=serializer)

    def hardware_list(self, context, values):
        """Signal the agent to find local hardware."""
        pass

    def fpga_program(self, context, accelerator, firmware_uuid):
        """Program a FPGA region, image can be a url or local file.
        
        :param context: request context.
        :param accelerator: FPGA object for programing
        :param firmware_uuid: The uuid of FPGA firmware
        :returns: program a FPGA object
        """
        cctxt = self.client.prepare(topic=self.topic,
                                    server=_compute_host(None, accelerator))
        return cctxt.call(context, 'fpga_program', accelerator=accelerator,
                          firmware_uuid=firmware_uuid)
