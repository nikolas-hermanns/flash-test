'''
Created on Feb 27, 2016

@author: enikher
'''
import os
import shutil as python_shutil
import utils.processutils as putils
from utils.log import log_enter_exit
from wheel import paths


class shutil():
    '''
    classdocs
    '''
    @log_enter_exit
    @staticmethod
    def mkdir_if_not_exsist(path):
        putils.execute(["mkdir", "-p", path])

    @log_enter_exit
    @staticmethod
    def copy(src, dst):
        if os.path.isfile(src):
            python_shutil.copy(src, dst)
        else:
            putils.execute(['cp', '-R', src, dst])

    @log_enter_exit
    @staticmethod
    def rm(path):
        putils.execute(["rm -rf", path])

    @log_enter_exit
    @staticmethod
    def mv(src, dst):
        putils.execute(["mv", src, dst])

    @log_enter_exit
    @staticmethod
    def get_all_files_in_path(path):
        if os.path.exists(path):
            file_list = putils.execute(['l', path])
            
