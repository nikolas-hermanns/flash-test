'''
Created on Mar 3, 2016

@author: enikher
'''
import unittest
from flash_test.utils.node import Node
from flash_test.utils.ssh_client import SSHClient
from flash_test.utils.processutils import execute


class SSHTest():

    def ls_on_localhost_thorugh_ssh(self):
        node = Node("localhost", address="localhost")
        localhost = SSHClient(node)
        ssh_ls = localhost.execute(["ls"])
        ls = execute(["ls ~"], shell=True)
        self.assertEqual(ssh_ls, ls)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'SSHTest.ls_on_localhost_thorugh_ssh']
    unittest.main()
