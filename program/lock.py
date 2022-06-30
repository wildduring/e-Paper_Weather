#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import time
import logging
logging.basicConfig(level=logging.DEBUG)

class LOCK():
    def __init__(self):
        self.__lock_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lock')
        if(os.path.exists(self.__lock_path)):    #检测lock文件夹
            ls = os.listdir(self.__lock_path)    #若文件夹存在，清空文件夹进行初始化
            for i in ls:
                c_path = os.path.join(self.__lock_path, i)
                if (not os.path.isdir(c_path)):
                    os.remove(c_path)
        else:
            os.mkdir(self.__lock_path)    #若不存在，创建文件夹

    def lock(self, lockname = "lock"):
        while(os.path.exists(os.path.join(self.__lock_path, lockname))):    #检测是否被锁定
            time.sleep(1)    #若被锁定，等待解锁
            logging.info("Waiting...")
        os.mknod(os.path.join(self.__lock_path, lockname))    #创建锁定标志

    def unlock(self, unlockname = "lock"):
        os.remove(os.path.join(self.__lock_path, unlockname))    #删除锁定标志

    def __del__(self):
        ls = os.listdir(self.__lock_path)    #若文件夹存在，清空文件夹
        for i in ls:
            c_path = os.path.join(self.__lock_path, i)
            if (not os.path.isdir(c_path)):
                os.remove(c_path)
