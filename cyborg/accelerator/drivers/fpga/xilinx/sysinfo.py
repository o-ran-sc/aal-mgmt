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

import json
import re
import subprocess

from cyborg.common import exception


VENDER_ID = "10ee"

FPGA_FLAGS = ["Memory controller", "Xilinx"]
FPGA_INFO_PATTERN = re.compile("(?P<devices>[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-9a-fA-F]) (?P"
                               "<name>.*) \[.* [\[](?P<vendor_id>[0-9a-fA-F]{4})"
                               ":(?P<product_id>[0-9a-fA-F]{4})].*")


def all_fpgas():
    pass


def fpga_tree():
    cmd = "sudo lspci -nnn | grep -E '%s'"
    cmd = cmd % "|".join(FPGA_FLAGS)
    if VENDER_ID:
        cmd = cmd + "| grep " + VENDER_ID
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    p.wait()
    fpgas = p.stdout.readlines()
    fpga_list = []
    for fpga in fpgas:
        m = FPGA_INFO_PATTERN.match(fpga)
        if m:
            fpga_dict = m.groupdict()
            if _get_shell_type(_get_shell_id(fpga_dict['devices'])) == \
                    'Lenovo_thinkcloud':
                if fpga_dict['devices'].endswith('.0'):
                    continue
                    # fpga_dict["function"] = ""
                    # fpga_dict["programable"] = False
                    # fpga_dict["assignable"] = False
                else:
                    fpga_dict["function"] = _get_role_function(
                        _get_shell_id(fpga_dict['devices']), fpga_dict['devices'])
                    fpga_dict["programable"] = True
                    fpga_dict["assignable"] = True
                fpga_dict["type"] = "FPGA"
                fpga_dict["devices"] = _match_nova_addr(fpga_dict["devices"])
                fpga_list.append(fpga_dict)
    return fpga_list


def program(device_addr, firmware_path):
    role_pciid = _reduce_orig_addr(device_addr)
    shell_pciid = _get_shell_id(role_pciid)
    return _program(shell_pciid, role_pciid, firmware_path)


def verify(device_addr):
    role_pciid = _reduce_orig_addr(device_addr)
    shell_pciid = _get_shell_id(role_pciid)
    return _verify(shell_pciid, role_pciid)

def get_function(device_addr):
    return _get_role_function(_get_shell_id(_reduce_orig_addr(device_addr)),
                              _reduce_orig_addr(device_addr))

def _exec_shell_role(command):
    try:
        p = subprocess.Popen("sudo shell_role %s" % command,
                             stdout=subprocess.PIPE, shell=True)
        p.wait()
    except Exception:
        raise exception.ShellExecFailed()
    stdout = p.stdout.readline()
    result = json.loads(stdout)
    if result['result'] == 'failed':
        raise exception.ShellReturnFailed()
    return result


def _get_shell_type(shell_pciid):
    result = _exec_shell_role("shell_type %s" % shell_pciid)
    return None if result['result'] == 'not found' else result['result']


def _get_role_function(shell_pciid, role_pciid):
    result = _exec_shell_role("get_function %s %s" % (shell_pciid, role_pciid))
    return result['ID'] if result['result'] == 'custom' else result['result']


def _program(shell_pciid, role_pciid, firmware_path):
    result = _exec_shell_role("program %s %s %s" %
                              (shell_pciid, role_pciid, firmware_path))
    if result['result'] == 'success':
        return True


def _verify(shell_pciid, role_pciid):
    result = _exec_shell_role("verify %s %s" % (shell_pciid, role_pciid))
    if result['result'] == 'true':
        return True
    elif result['result'] == 'false':
        return False


def _get_shell_id(role_pciid):
    return role_pciid[:-1] + '0'


def _match_nova_addr(devices):
    addr = '0000:'+devices.replace(".", ":")
    return addr


def _reduce_orig_addr(nova_addr):
    addr = nova_addr[5:][::-1].replace(':', '.', 1)[::-1]
    return addr
