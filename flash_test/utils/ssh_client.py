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
        cmd = ['ssh', '-i', SshUtil.get_id_rsa(), '-F',
               SshUtil.get_config_file_path(),
               self.node.name]
        if self.node.password:
            cmd = ['sshpass', '-p', self.node.password] + cmd
        if not self.node.has_access:
            with open(SshUtil.get_id_rsa() + ".pub") as pub_key_file:
                pub_key = pub_key_file.read()
                try:
                    cmd.append('echo %s >> ~/.ssh/authorized_keys'
                               % pub_key)
                    execute(cmd)
                except Exception:
                    self.node.jump.execute(
                        'ssh %s '
                        '\'echo %s >> ~/.ssh/authorized_keys\''
                        % (self.node.address, pub_key))
            self.node.has_access = True
        cmd.append(command_as_string)
        return execute(cmd, **kwargs)
