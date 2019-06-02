# Copyright 2018 Lenovo, Inc.
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


"""
Cyborg Intel Co-processor driver implementation.
"""

from cyborg.accelerator.drivers.co_processor.base import Co_processorDriver
from cyborg.accelerator.drivers.co_processor.intel import sysinfo


class INTEL_Co_processorDriver(Co_processorDriver):
    """Base class for Co_processor drivers.

       This is just a virtual Co_processor drivers interface.
       Vedor should implement their specific drivers.
    """
    VENDOR = "intel"

    def __init__(self, *args, **kwargs):
        pass

    def discover(self):
        return sysinfo.co_processor_tree()

    def program(self, device_path, image):
        pass
