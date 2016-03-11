'''
Created on Mar 3, 2016

@author: enikher
'''
from flash_test.utils.ssh_client import SSHClient
from flash_test.utils.ssh_util import SshUtil


class Node(object):
    '''
    classdocs
    '''

    def __init__(self, name, address=None, port=None,
                 user=None, password=None, jump=None, dic=None):
        self.name = name
        self.address = address
        self.jump = jump
        self.user = user
        self.password = password
        if dic:
            self.read_from_dic(dic)
        self.sshc = SSHClient(self)

    def read_from_dic(self, dic):
        for (key, value) in dic.iteritems():
            exec("self.%s = '%s'" % (key, value))

    def ping(self, ip):
        self.execute(['ping', '-c', '1', ip])

    def execute(self, cmd, **kwargs):
        return self.sshc.execute(cmd, **kwargs)

    def to_ssh_config(self):
        config = ["Host %s" % self.name,
                  "    Hostname %s" %
                  (self.address if self.address else self.name)]
        if self.jump:
            config.append("    ProxyCommand ssh -F %(config_path)s "
                          "-W %%h:%%p %(name)s"
                          % {'config_path': SshUtil.get_config_file_path(),
                             'name': self.jump.name})
        if self.user:
            config.append("    user %s" % self.user)
        return '\n'.join(config)
