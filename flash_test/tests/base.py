# Copyright (c) 2016 Ericsson.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import base64
import six
from oslo_utils import encodeutils
from tempest.common.utils import data_utils
from oslo_log import log as logging
from tempest import config
import tempest.test
from flash_test.openstack.openstack_env import OpenstackEnv
CONF = config.CONF

LOG = logging.getLogger(__name__)
FLASH_TEST_BRIDGE_NAME = "br-flash_test"


class BaseFlashTest(tempest.test.BaseTestCase):
    """Base Class for all FlashTests

    """

    @classmethod
    def resource_setup(cls):
        openstack_env = OpenstackEnv
        openstack_env.resource_setup()
        super(BaseFlashTest, cls).resource_setup()
        cls.hypervisor_br_added = []

    @classmethod
    def resource_cleanup(cls):
        for hypervisor in cls.hypervisor_br_added:
            hypervisor.execute(["ifconfig", "br-flash_test", "down"])
            hypervisor.execute(["brctl", "delbr", "br-flash_test"])
        super(BaseFlashTest, cls).resource_cleanup()

    @classmethod
    def get_flash_vm_user_data(cls, interface, ip):
        # Wait for flash interface to come up
        userdata = ["#!/bin/sh",
                    "while true;do",
                    ("if [[ \"$(ifconfig -a |grep %s)\" != \"\" ]];then"
                     % interface),
                    "break",
                    "fi",
                    "sleep 10",
                    "done",
                    ("sudo ifconfig %s %s up"
                     % (interface, ip))]
        userdata = "\n".join(userdata)

        # This section is copied from python-novaclient
        # NOTE(melwitt): Text file data is converted to bytes prior to
        # base64 encoding. The utf-8 encoding will fail for binary files.
        if six.PY3:
            try:
                userdata = userdata.encode("utf-8")
            except AttributeError:
                # In python 3, 'bytes' object has no attribute 'encode'
                pass
        else:
            try:
                userdata = encodeutils.safe_encode(userdata)
            except UnicodeDecodeError:
                pass
        return base64.b64encode(userdata).decode('utf-8')

    @classmethod
    def make_flash_connection(cls, hypervisor, server):
        if hypervisor not in cls.hypervisor_br_added:
            (value, err) = hypervisor.execute(['brctl', 'show',
                                               FLASH_TEST_BRIDGE_NAME])
            if err and 'can\'t get info No such device' in err:
                hypervisor.execute(['brctl', 'addbr', FLASH_TEST_BRIDGE_NAME])
                hypervisor.execute(['ifconfig', FLASH_TEST_BRIDGE_NAME,
                                    '10.19.87.254/24', 'up'])
            cls.hypervisor_br_added.append(hypervisor)
        hypervisor.execute(['virsh', 'attach-interface',
                            server['OS-EXT-SRV-ATTR:instance_name'],
                            'bridge', FLASH_TEST_BRIDGE_NAME])
