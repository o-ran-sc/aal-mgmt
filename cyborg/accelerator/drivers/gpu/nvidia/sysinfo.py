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
Cyborg Intel GPU driver implementation.
"""

from cyborg.accelerator.drivers.gpu import utils

import subprocess


VENDER_ID = "10de"


def all_gpus():
    pass


def gpu_tree():
    # devs = utils.discover_gpus(VENDER_ID)
    # return devs
    cmd = "sudo lspci -nnn | grep -E '%s'"
    cmd = cmd % "|".join(utils.GPU_FLAGS)
    if VENDER_ID:
        cmd = cmd + "| grep " + VENDER_ID
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    p.wait()
    gpus = p.stdout.readlines()
    gpu_list = []
    for gpu in gpus:
        m = utils.GPU_INFO_PATTERN.match(gpu)
        if m:
            gpu_dict = m.groupdict()
            gpu_dict["type"] = "GPU"
            gpu_dict["devices"] = _match_nova_addr(gpu_dict["devices"])
            gpu_dict["assignable"] = True
            gpu_dict["programable"] = False
            gpu_list.append(gpu_dict)
    return gpu_list


def _match_nova_addr(devices):
    addr = '0000:'+devices.replace(".", ":")
    return addr
