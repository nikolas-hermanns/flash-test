'''
Created on Mar 3, 2016

@author: enikher
'''
from processutils import execute
from flash_test.utils.ssh_util import SshUtil


class SSHClient(object):
    '''
    classdocs
    '''
    def __init__(self, node):
        self.node = node

    def execute(self, cmd, **kwargs):
        from flash_test.openstack.openstack_env import OpenstackEnv
        OpenstackEnv.gen_ssh_config(self.node)
        command_as_string = ' '.join(cmd)
        cmd = ['ssh', '-F', SshUtil.get_config_file_path(),
               self.node.name, command_as_string]
        if self.node.password:
            cmd = ['sshpass', '-p', self.node.password] + cmd
        return execute(cmd, **kwargs)
