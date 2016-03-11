'''
Created on Mar 11, 2016

@author: enikher
'''
from tempest.api.compute import base as compute_base
from flash_test.tests import base
from flash_test.openstack.openstack_env import OpenstackEnv
from flash_test.utils.node import Node
import time
from tempest.lib.api_schema.response.compute.v2_1.servers import delete_server
SERVER_REACHABLE_TIMEOUT = 300


class BaseFlashComputeTest(compute_base.BaseV2ComputeAdminTest,
                           base.BaseFlashTest):
    '''
    classdocs
    '''
    @classmethod
    def resource_setup(cls):
        super(BaseFlashComputeTest, cls).resource_setup()
        # Use the admin user to be able to give an availability zone
        cls.os_normal = cls.os
        cls.os = cls.os_adm

        cls.flash_servers = []

    @classmethod
    def resource_cleanup(cls):
        for servers in cls.flash_servers:
            cls.delete_server(servers.openstack_info['id'])
        super(BaseFlashComputeTest, cls).resource_cleanup()

    @classmethod
    def delete_server(cls, server_id):
        # Since we are using the admin tenant servers have to be delete
        # another way as tempest is doing that normally
        OpenstackEnv.delete_server(server_id)

    @classmethod
    def create_test_server(cls, volume_backed=False, **kwargs):
        # All flash test os_server are validatable through their own
        # connectivity
        if 'validatable' in kwargs:
            kwargs.pop('validatable')
        if 'userdata' in kwargs:
            raise Exception("Additional userdata is not "
                            "supported at the moment")
        userdata = cls.get_flash_vm_user_data("eth1", "10.19.87.20")
        os_server = super(BaseFlashComputeTest, cls
                          ).create_test_server(
            validatable=False,
            volume_backed=volume_backed,
            wait_until='ACTIVE',
            config_drive='True',
            user_data=userdata,
            **kwargs)
        # Get hypervisor
        os_server = cls.os_adm.servers_client.show_server(
                              os_server['id'])['server']
        hypervisor_name = os_server['OS-EXT-SRV-ATTR:host']
        hypervisor = OpenstackEnv.hypervisors[hypervisor_name]
        cls.make_flash_connection(hypervisor, os_server)
        flash_server = Node(name=os_server['id'], address='10.19.87.20',
                            user='cirros', password='cubswin:)',
                            jump=hypervisor)
        flash_server.openstack_info = os_server
        # availability_zone = hypervisor
        # availability_zone='nova:node-5.opnfv.org'
        # normal user cls.servers_client.show_server(os_server['id'])
        cls.flash_servers.append(flash_server)
        return flash_server

    def wait_until_server_is_reachable(self, server):
        start = time.time()
        last_exception = None
        while time.time() < start + SERVER_REACHABLE_TIMEOUT:
            try:
                server.execute(['ls'])
                return
            except Exception as ex:
                last_exception = ex
                time.sleep(10)
        raise last_exception
