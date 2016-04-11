'''
Created on Mar 11, 2016

@author: enikher
'''
from flash_test.utils.node import Node
from flash_test.utils.ssh_util import SshUtil
from tempest.api.compute import base as compute_base
import os
import yaml
from novaclient.client import Client as nova
from novaclient import api_versions

FLASH_TEST_CONFIG_YAML = "/etc/flash_test.yaml"


class OpenstackEnv(object):

    # These clients are only used to create the environment
    # In general the tempest clients shall be used.
    _novacl = nova(api_versions.APIVersion("2.0"),
                   os.environ['OS_USERNAME'],
                   os.environ['OS_PASSWORD'],
                   os.environ['OS_TENANT_NAME'],
                   auth_url=os.environ['OS_AUTH_URL'])
    hypervisors = {}
    env_nodes = []
    main_controller = None

    @classmethod
    def resource_setup(cls):
        if os.path.isfile(FLASH_TEST_CONFIG_YAML):
            with open(FLASH_TEST_CONFIG_YAML) as f:
                cls.config = yaml.load(f)
        else:
            raise Exception("Config: %s is not found."
                            % FLASH_TEST_CONFIG_YAML)
        # add all nodes
        for (name, node) in cls.config['env']['nodes'].iteritems():
            new_node = Node(name, node)
            cls.env_nodes.append(new_node)
            if name == "main_controller":
                cls.main_controller = new_node

        # All openstack hypervisors
        nova_hypervisors = cls._novacl.hypervisors.list()
        for nova_hypervisor in nova_hypervisors:
            new_hypervisor = Node(
                name=nova_hypervisor.hypervisor_hostname,
                address=nova_hypervisor.host_ip,
                user=cls.config['env']['hypervisor_ssh_user'],
                jump=cls.main_controller)
            cls.hypervisors[nova_hypervisor.hypervisor_hostname] =\
                new_hypervisor
            cls.env_nodes.append(new_hypervisor)

    @classmethod
    def gen_ssh_config(cls, node):
        if node not in cls.env_nodes:
            cls.env_nodes.append(node)
        SshUtil.gen_ssh_config(cls.env_nodes)

    @classmethod
    def delete_server(cls, serverid):
        cls._novacl.servers.delete(serverid)

