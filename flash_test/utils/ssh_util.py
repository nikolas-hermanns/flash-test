'''
Created on Mar 14, 2016

@author: enikher
'''
TMP_SSH_CONFIG = "/tmp/flash_test_ssh_config"
import os

class SshUtil(object):

    @staticmethod
    def gen_ssh_config(node_list):
        config = ["UserKnownHostsFile=/dev/null",
                  "StrictHostKeyChecking=no",
                  "ForwardAgent yes",
                  "GSSAPIAuthentication=no",
                  "LogLevel ERROR"]
        for node in node_list:
            config.append(node.to_ssh_config())
        with open(TMP_SSH_CONFIG, 'w') as f:
            f.write('\n'.join(config))

    @staticmethod
    def get_config_file_path():
        return TMP_SSH_CONFIG

    @staticmethod
    def get_id_rsa():
        home = os.getenv("HOME")
        return ("%s/.ssh/id_rsa" % home)
