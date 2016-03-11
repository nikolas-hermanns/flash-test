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

from flash_test.openstack.compute import BaseFlashComputeTest as base
from flash_test.openstack.openstack_env import OpenstackEnv
from oslo_log import log as logging


LOG = logging.getLogger(__name__)


class PingTest(base):
    """TODO
    """

    @classmethod
    def setup_clients(cls):
        super(PingTest, cls).setup_clients()

    @classmethod
    def resource_cleanup(cls):
        super(PingTest, cls).resource_cleanup()

    def test_server(self):
        server = self.create_test_server(volume_backed=False)
        self.wait_until_server_is_reachable(server)

    def test_ping_2_servers(self):
        server1 = self.create_test_server(volume_backed=False,
                                          availability_zone='nova:%s'
                                          % OpenstackEnv.hypervisors.items()[0][0])
        server2 = self.create_test_server(volume_backed=False,
                                          availability_zone='nova:%s'
                                          % OpenstackEnv.hypervisors.items()[1][0])
        self.wait_until_server_is_reachable(server1)
        self.wait_until_server_is_reachable(server2)
        ip = server2.openstack_info['addresses'].items()[0][1][0]['addr']
        server1.ping(ip)

    def test_ping_one_vm_on_all_hosts(self):
        servers = []
        for (name, hypervisor) in OpenstackEnv.hypervisors.iteritems():
            servers.append(self.create_test_server(volume_backed=False,
                                                   availability_zone='nova:%s'
                                                   % hypervisor.name))
        ip_server_dict = {}
        for server in servers:
            self.wait_until_server_is_reachable(server)
            ip_server_dict[(server.openstack_info['addresses'].items()[0][1][0]['addr'])] = server
        atleast_one_failed = False
        for server in servers:
            for ip in ip_server_dict:
                try:
                    server.ping(ip)
                except Exception:
                    atleast_one_failed = True
                    LOG.error("Server: %(src_server)s was not able to "
                              "reach Server: %(dst_server)s." %
                              {'src_server': server.openstack_info['id'],
                               'dst_server': ip_server_dict[ip].openstack_info['id']})
                    pass
        if atleast_one_failed:
            raise Exception("At least on server could not reach another "
                            "server.")

    def test_hypervisor_reachable(self):
        ips = []
        for (name, hypervisor) in OpenstackEnv.hypervisors.iteritems():
            ips.append(hypervisor.address)
        for (name, hypervisor) in OpenstackEnv.hypervisors.iteritems():
            for ip in ips:
                hypervisor.ping(ip)

