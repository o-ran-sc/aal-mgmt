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
Utils for Co-processor driver.
"""

import re
import subprocess

# Co-processor.*QAT use to match for intel QAT 8950 card
# Co-processor.*Intel Corporation Device use to match for intel QAT 8970 card

Co_processor_pf_FLAGS = ["00.0 Co-processor.*QAT|"
                         "00.0 Co-processor.*Intel Corporation Device"]
Co_processor_FLAGS = ["Co-processor.*QAT Virtual Function|"
                      "Co-processor.*Intel Corporation Device"]
Co_processor_INFO_PATTERN = re.compile("(?P<devices>[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-9a-fA-F]) (?P"
                              "<name>.*) \[.* [\[](?P<vendor_id>[0-9a-fA-F]{4})"
                              ":(?P<product_id>[0-9a-fA-F]{4})].*")


def discover_vendors():
    cmd = "sudo lspci -nnn | grep -E '%s'"
    cmd = cmd % "|".join(Co_processor_pf_FLAGS)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    p.wait()
    co_processors = p.stdout.readlines()
    vendors = set()
    for co_processor in co_processors:
        m = Co_processor_INFO_PATTERN.match(co_processor)
        if m:
            vendor_id = m.groupdict().get("vendor_id")
            vendors.add(vendor_id)
    return vendors
