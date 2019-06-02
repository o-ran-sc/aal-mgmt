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

import subprocess
from cyborg.accelerator.drivers.co_processor import utils


VENDER_ID = "8086"


def all_co_processors():
    pass


def co_processor_tree():
    cmd = "sudo lspci -nnn | grep -E '%s'"
    cmd = cmd % "|".join(utils.Co_processor_FLAGS)
    if VENDER_ID:
        cmd = cmd + "| grep " + VENDER_ID
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    p.wait()
    co_processors = p.stdout.readlines()
    co_processors_list = []
    for co_processor in co_processors:
        m = utils.Co_processor_INFO_PATTERN.match(co_processor)
        if m:
            co_processor_dict = m.groupdict()
            co_processor_dict["type"] = "Co-processor"
            co_processor_dict["function"] = "QAT"
            co_processor_dict["devices"] = _match_nova_addr(co_processor_dict["devices"])
            co_processor_dict["assignable"] = True
            co_processor_dict["programable"] = False
            co_processors_list.append(co_processor_dict)
    return co_processors_list


def _match_nova_addr(devices):
    addr = '0000:'+devices.replace(".", ":")
    return addr
