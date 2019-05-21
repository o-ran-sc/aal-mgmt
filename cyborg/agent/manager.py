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

import os
import time
import thread

import oslo_messaging as messaging
from oslo_service import periodic_task
from oslo_config import cfg

from cyborg.accelerator.drivers.fpga.base import FPGADriver
from cyborg.accelerator.drivers.gpu.base import GPUDriver
from cyborg.agent.resource_tracker import ResourceTracker
from cyborg.conductor import rpcapi as conductor_api

from cyborg import objects

from cyborg.common import exception
from cyborg.conf import CONF
from cyborg import image
from oslo_log import log as logging


fpga_opts={
    cfg.IntOpt('program_check_interval',
               default=10,
               help='DEPRECATED: FPGA program status check interval '),
    cfg.IntOpt('program_retry_count',
               default=6,
               help='DEPRECATED: FPGA program status check retry count '),
    cfg.StrOpt('firmware_cache_folder',
                default='/tmp/firmware_cache/',
                help='DEPRECATED: The cache folder path on host to download FPGA firmware')
}

LOG = logging.getLogger(__name__)
CONF = cfg.CONF
CONF.register_opts(fpga_opts, 'fpga')

class AgentManager(periodic_task.PeriodicTasks):
    """Cyborg Agent manager main class."""

    RPC_API_VERSION = '1.0'
    target = messaging.Target(version=RPC_API_VERSION)

    def __init__(self, topic, host=None):
        super(AgentManager, self).__init__(CONF)
        #can only use in the same node, change it to RPC to conductor
        self.conductor_api = conductor_api.ConductorAPI()
        self.image_api = image.API()
        self.topic = topic
        self.host = host or CONF.host
        self.fpga_driver = FPGADriver()
        self._rt = ResourceTracker(host, self.conductor_api)
        self.gpu_driver = GPUDriver()
        if CONF.fpga.firmware_cache_folder:
            self.firmware_folder = CONF.fpga.firmware_cache_folder
        else:
            self.firmware_folder = '/tmp/firmware_cache/'
        self.program_check_interval = CONF.fpga.program_check_interval
        self.program_retry_count = CONF.fpga.program_retry_count

    def periodic_tasks(self, context, raise_on_error=False):
        return self.run_periodic_tasks(context,raise_on_error=raise_on_error)

    def hardware_list(self, context, values):
        """List installed hardware."""
        pass

    def fpga_program(self, context, accelerator, firmware_uuid):
        """Program a FPGA region, image can be a url or local file."""
        # And add claim and rollback logical
        tmp_file_path = self.firmware_folder + str(firmware_uuid)
        file_name = str(firmware_uuid)
        driver = self.fpga_driver.create(accelerator.vendor)
        self._fpga_program_precommit(context, driver, accelerator,
                                     firmware_uuid, self.firmware_folder,
                                     file_name)
        LOG.info('Start to download firmware %s into %s ' % (firmware_uuid, accelerator))

        thread.start_new_thread(self._fpga_program_postcommit,
                                (context, driver, accelerator, firmware_uuid))

    @periodic_task.periodic_task(spacing=CONF.periodic_interval)
    def update_available_resource(self, context):
        """update all kinds of accelerator resources from their drivers."""
        '''
        driver = netronome.NETRONOMEDRIVER()
        port_resource = driver.get_available_resource()
        if port_resource:
            self.conductor_api.port_bulk_create(context, port_resource)
        '''
        # Todo resolve conflict between intel and xilinx
        # There was a conflict between intel fpga and xilinx fpga resource
        # tracker, annotate the following line until the conflict resolved
        # self._rt.update_usage(context)
        self._rt.update_gpu_usage(context)
        self._rt.update_co_processor_usage(context)
        self._rt.updage_xilinx_fpge_usage(context)

    def _fpga_program_precommit(self, context, driver, accelerator,
                                firmware_uuid, file_path, file_name):
        """
        Prepare local firmware file and change accelerator status into in_use.
        Call driver api to program firmware.
        
        :param context: request context
        :param accelerator: fpga object for programing firmware
        :param firmware_uuid: the firmware uuid
        :param file_path: local tmp folder path
        :param file_name: local tmp file name
        """

        if not os.path.exists(file_path):
            os.mkdir(file_path)
        tmp_file_path = file_path + str(file_name)
        self.image_api.download(context, firmware_uuid, dest_path=tmp_file_path)

        accelerator.assignable = False
        accelerator.availability = 'in-programing'
        accelerator.save(context)
        try:
            driver.program(accelerator, tmp_file_path)
        except NotImplementedError:
            accelerator.assignable = True
            accelerator.availability = 'free'
            accelerator.save(context)
            raise
        except Exception:
            accelerator.availability = 'error'
            accelerator.save(context)
            raise

    def _fpga_program_postcommit(self, context, driver, accelerator, firmware_uuid):
        """
        Periodical check firmware program status. And update accelerator status when program success.
        
        :param context: request context
        :param accelerator: fpga object for programing firmware
        :param firmware_uuid: the firmware uuid 
        """
        program_result = False
        check_interval = self.program_check_interval
        retry_count = self.program_retry_count
        while retry_count != 0:
            try:
                program_result = driver.check_program_status(accelerator)
            except exception.ShellExecFailed:
                break
            if program_result:
                break
            time.sleep(check_interval)
            retry_count -= 1
        self._update_fpga_status(context, driver, accelerator, firmware_uuid, program_result)

    def _update_fpga_status(self, context, driver, accelerator, firmware_uuid, result):
        if result:
            accelerator.assignable = True
            accelerator.availability = 'free'
            accelerator.function = driver.get_function(accelerator)
            LOG.info('Success to download firmware %s into %s ' % (firmware_uuid, accelerator))
        else:
            accelerator.availability = 'error'
            LOG.error('Failed to download firmware %s into %s ' % (firmware_uuid, accelerator))
        accelerator.save(context)
