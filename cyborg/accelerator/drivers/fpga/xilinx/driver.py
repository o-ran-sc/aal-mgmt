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
Cyborg Xilinx FPGA driver implementation.
"""

from cyborg.accelerator.drivers.fpga.base import FPGADriver
from cyborg.accelerator.drivers.fpga.xilinx import sysinfo


class XilinxFPGADriver(FPGADriver):
    """Base class for Xilinx FPGA drivers.

       This is just a virtual Xilinx FPGA drivers interface.
       Vedor should implement their specific drivers.
    """

    VENDOR = "xilinx"

    def __init__(self, *args, **kwargs):
        pass

    def discover(self):
        return sysinfo.fpga_tree()

    def program(self, device_path, image):
        return sysinfo.program(device_path.pcie_address, image)

    def check_program_status(self, device):
        return sysinfo.verify(device.pcie_address)

    def get_function(self, device):
        return sysinfo.get_function(device.pcie_address)
