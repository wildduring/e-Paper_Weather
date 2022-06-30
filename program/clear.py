#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import logging
import time

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')   #水墨屏显示库

if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd2in13bc

logging.basicConfig(level=logging.DEBUG)

#水墨屏初始化
epd = epd2in13bc.EPD()
logging.info("init and Clear")
epd.init()
epd.Clear()
time.sleep(1)
epd2in13bc.epdconfig.module_exit()
exit()
