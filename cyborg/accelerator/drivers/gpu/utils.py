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
Utils for GPU driver.
"""

import re
import subprocess


GPU_FLAGS = ["VGA compatible controller", "3D controller"]
GPU_INFO_PATTERN = re.compile("(?P<devices>[0-9]{2}:[0-9]{2}\.[0-9]) (?P"
                              "<name>.*) \[.* [\[](?P<vendor_id>[0-9a-fA-F]{4})"
                              ":(?P<product_id>[0-9a-fA-F]{4})].*")


def discover_vendors():
    cmd = "sudo lspci -nnn | grep -E '%s'"
    cmd = cmd % "|".join(GPU_FLAGS)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    p.wait()
    gpus = p.stdout.readlines()
    vendors = set()
    for gpu in gpus:
        m = GPU_INFO_PATTERN.match(gpu)
        if m:
            vendor_id = m.groupdict().get("vendor_id")
            vendors.add(vendor_id)
    return vendors
