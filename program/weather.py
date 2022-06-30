#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

medir = os.path.dirname(os.path.realpath(__file__))  #当前文件夹
bmpdir = os.path.join(medir, 'bmps')  #天气图标库
cfgdir = os.path.join(medir, 'config')  #配置文件库
libdir = os.path.join(medir, 'lib')   #水墨屏显示库
logdir = os.path.join(medir, 'weather_log')   #水墨屏显示库

if os.path.exists(libdir):
    sys.path.append(libdir)

import requests
import json
import time
import socket
from PIL import Image,ImageDraw,ImageFont
from waveshare_epd import epd2in13bc
import struct
import smbus
import RPi.GPIO as GPIO
import lock

import logging
logging.basicConfig(level=logging.DEBUG)

#水墨屏初始化
epd = epd2in13bc.EPD()
logging.info("init and Clear")
epd.init()
epd.Clear()
time.sleep(1)

HBimage = Image.new('1', (212, 104), 255)  #黑色部分画布
HRimage = Image.new('1', (212, 104), 255)  #红色部分画布
white = Image.new('1', (212, 104), 255) #白色底色
drawblack = ImageDraw.Draw(HBimage) #黑色部分笔刷
drawred = ImageDraw.Draw(HRimage)   #红色部分笔刷
font20 = ImageFont.truetype(os.path.join(bmpdir, 'Font.ttc'), 20)   #创建字体
font18 = ImageFont.truetype(os.path.join(bmpdir, 'Font.ttc'), 18)   #创建字体
font16 = ImageFont.truetype(os.path.join(bmpdir, 'Font.ttc'), 16)   #创建字体
font14 = ImageFont.truetype(os.path.join(bmpdir, 'Font.ttc'), 14)   #创建字体
font12 = ImageFont.truetype(os.path.join(bmpdir, 'Font.ttc'), 12)   #创建字体
font10 = ImageFont.truetype(os.path.join(bmpdir, 'Font.ttc'), 10)   #创建字体
font8 = ImageFont.truetype(os.path.join(bmpdir, 'Font.ttc'), 8)   #创建字体
font6 = ImageFont.truetype(os.path.join(bmpdir, 'Font.ttc'), 6)   #创建字体
network = False    #网络状态
locker = lock.LOCK()

#UPS初始化
def QuickStart(bus):
        address = 0x36
        bus.write_word_data(address, 0x06,0x4000)

def PowerOnReset(bus):
        address = 0x36
        bus.write_word_data(address, 0xfe,0x0054)

def readVoltage(bus):
        "This function returns as float the voltage from the Raspi UPS Hat via the provided SMBus object"
        address = 0x36
        read = bus.read_word_data(address, 0X02)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        voltage = swapped * 1.25 /1000/16
        return voltage

def readCapacity(bus):
        "This function returns as a float the remaining capacity of the battery connected to the Raspi UPS Hat via the provided SMBus object"
        address = 0x36
        read = bus.read_word_data(address, 0X04)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        capacity = swapped/256
        #capacity = 10
        return capacity if capacity <= 100 else 100

#UPS初始化
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(4,GPIO.IN)
bus = smbus.SMBus(1)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
PowerOnReset(bus)
QuickStart(bus)

def check_battery():    #检测电池电量
    logging.info("Voltage:%5.2fV" % readVoltage(bus))
    logging.info("Battery:%5i%%" % readCapacity(bus))
    if (readCapacity(bus) == 100):
        logging.info("Battery FULL")
    if (readCapacity(bus) < 5):
        logging.info("Battery LOW")
    if (GPIO.input(4) == GPIO.HIGH):
        logging.info("Power Adapter Plug In ")
    if (GPIO.input(4) == GPIO.LOW):
        logging.info("Power Adapter Unplug")

def isNetOK(testserver):    #判断是否联网
    s=socket.socket()
    s.settimeout(3)
    try:
        status = s.connect_ex(testserver)
        if status == 0:
            s.close()
            return True
        else:
            return False
    except Exception as e:
        return False

def read_local_weather_info(JSON_pass):#    读取本地天气JSON备份
    if(os.path.exists(JSON_pass)):    #判断JSON备份是否存在
        with open(JSON_pass,'r') as load_f:
            weather_info = json.load(load_f)
        return weather_info
    else:
        return False

def get_weather_info(extensions):
    global network
    network = isNetOK(testserver=('restapi.amap.com',443))
    if(network):   #网络连接正常
        locker.lock("citycode")
        with open(os.path.join(cfgdir, 'city_code.ini'), "r") as city_code:
            city = city_code.readline().replace('\n', '')    #城市码
            if(len(city)<6):
                city = "140702"    #若读取错误，强制显示榆次区的天气
        locker.unlock("citycode")
        locker.lock("usr_key")
        with open(os.path.join(cfgdir, 'usr_key.ini'), "r") as usr_key:
            key = usr_key.readline().replace('\n', '')    #用户密钥
        locker.unlock("usr_key")
        amap_weather_url = "https://restapi.amap.com/v3/weather/weatherInfo?city=" + city + "&key=" + key + "&extensions=" + extensions
        response = requests.get(url=amap_weather_url)   #访问网址获取天气
        weather_info = json.loads(response.text)
        if(weather_info["status"] == '1' and weather_info["infocode"] == "10000"):  #读入天气信息正常
            with open(os.path.join(logdir, 'weather_info_' + extensions + '_log.json'), "w") as f:    #打开JSON文件
                json.dump(weather_info, f)  #写入JSON备份文件
            return weather_info #返回天气信息
        else:
            return read_local_weather_info(os.path.join(logdir, 'weather_info_' + extensions + '_log.json'))
    else:
        return read_local_weather_info(os.path.join(logdir, 'weather_info_' + extensions + '_log.json'))

def show_on_epaper(blackimage, redimage):
    epd.init()
    epd.display(epd.getbuffer(blackimage), epd.getbuffer(redimage))
    logging.info("Goto Sleep...")
    epd.sleep()
    time.sleep(3)
    #epd.Dev_exit()

def point_coordinate(min_temp, max_temp, temp):
    # y = a*x+b
    # y = [16+20, 74]  纵轴范围，留出图标的空间，图标缩小到0.14倍
    # x = [max_temp, min_temp]
    a = (36.0-74.0)/(max_temp-min_temp)
    b = 36-a*max_temp
    return int(a*temp+b)    #分辨率低，此处取整误差较大

def show_weather(weather_info_base, weather_info_all):
    global network
    try:
        HBimage.paste(white, (0, 0))
        HRimage.paste(white, (0, 0))

        #weather_info_base = get_weather_info('base')   #获取当天天天气信息
        #weather_info_all = get_weather_info('all')   #获取未来三天天气信息

        main_wather_bmp = Image.open(os.path.join(bmpdir, weather_info_base["lives"][0]["weather"] + '.bmp')) #打开当天的天气图标
        main_wather_bmp = main_wather_bmp.resize((int(main_wather_bmp.size[0]*0.5), int(main_wather_bmp.size[1]*0.5)))  #将图标缩小到原来的0.5倍
        HRimage.paste(main_wather_bmp, (0,5))  #将当天的天气图标粘贴到(0, 5)的位置
        logging.info("main_wather_bmp.size:" + str(main_wather_bmp.size))
        drawblack.text((int((main_wather_bmp.size[0]-len(weather_info_all['forecasts'][0]['city'])*14)/2), main_wather_bmp.size[1]+5), weather_info_all['forecasts'][0]['city'], font = font14, fill = 0)   #绘制当前城市名称

        drawblack.text((78, 0), time.strftime('%Y-%m-%d  %a',time.localtime(time.time())), font = font14, fill = 0)   #绘制当前日期

        #绘制气温折线图
        drawred.line((74, 86, 204, 86), fill = 0)    #绘制横轴
        #第一个点
        drawred.line((90, 86, 90, 84), fill = 0)    #横轴上的点
        drawblack.text((88, 86), weather_info_all["forecasts"][0]['casts'][0]['date'][-2:] if weather_info_all["forecasts"][0]['casts'][0]['date'][-2:][0] != '-' else '0' + weather_info["forecasts"][0]['casts'][0]['date'][-2:][1], font = font8, fill = 0)  #点下方的日期
        #第二个点
        drawred.line((122, 86, 122, 84), fill = 0)    #横轴上的点
        drawblack.text((120, 86), weather_info_all["forecasts"][0]['casts'][1]['date'][-2:] if weather_info_all["forecasts"][0]['casts'][1]['date'][-2:][0] != '-' else '0' + weather_info["forecasts"][0]['casts'][1]['date'][-2:][1], font = font8, fill = 0)  #点下方的日期
        #第三个点
        drawred.line((154, 86, 154, 84), fill = 0)    #横轴上的点
        drawblack.text((152, 86), weather_info_all["forecasts"][0]['casts'][2]['date'][-2:] if weather_info_all["forecasts"][0]['casts'][2]['date'][-2:][0] != '-' else '0' + weather_info["forecasts"][0]['casts'][2]['date'][-2:][1], font = font8, fill = 0)  #点下方的日期
        #第四个点
        drawred.line((186, 86, 186, 84), fill = 0)    #横轴上的点
        drawblack.text((184, 86), weather_info_all["forecasts"][0]['casts'][3]['date'][-2:] if weather_info_all["forecasts"][0]['casts'][3]['date'][-2:][0] != '-' else '0' + weather_info["forecasts"][0]['casts'][3]['date'][-2:][1], font = font8, fill = 0)  #点下方的日期
        #绘制折线
        daytemp, nighttemp = [], []
        for i in weather_info_all["forecasts"][0]['casts']:
            daytemp.append(int(i['daytemp']))    #统计日间最高温
            nighttemp.append(int(i['nighttemp']))    #统计夜间最高温
        logging.info('Daytemp: ' + str(daytemp))
        logging.info('Nighttemp: ' + str(nighttemp))
        #先显示图标，防止图标覆盖掉折线
        #第一天天气图标
        day1bmp = Image.open(os.path.join(bmpdir, weather_info_all["forecasts"][0]["casts"][0]["dayweather"] + '.bmp')) #打开天气图标
        day1bmp = day1bmp.resize((int(day1bmp.size[0]*0.14), int(day1bmp.size[1]*0.14)))  #将图标缩小到原来的0.14倍
        HRimage.paste(day1bmp, (82,point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), daytemp[0])-20))
        #第二天天气图标
        day2bmp = Image.open(os.path.join(bmpdir, weather_info_all["forecasts"][0]["casts"][1]["dayweather"] + '.bmp')) #打开天气图标
        day2bmp = day2bmp.resize((int(day2bmp.size[0]*0.14), int(day2bmp.size[1]*0.14)))  #将图标缩小到原来的0.14倍
        HRimage.paste(day2bmp, (114,point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), daytemp[1])-20))
        #第三天天气图标
        day3bmp = Image.open(os.path.join(bmpdir, weather_info_all["forecasts"][0]["casts"][2]["dayweather"] + '.bmp')) #打开天气图标
        day3bmp = day3bmp.resize((int(day3bmp.size[0]*0.14), int(day3bmp.size[1]*0.14)))  #将图标缩小到原来的0.14倍
        HRimage.paste(day3bmp, (146,point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), daytemp[2])-20))
        #第四天天气图标
        day4bmp = Image.open(os.path.join(bmpdir, weather_info_all["forecasts"][0]["casts"][3]["dayweather"] + '.bmp')) #打开天气图标
        day4bmp = day4bmp.resize((int(day4bmp.size[0]*0.14), int(day4bmp.size[1]*0.14)))  #将图标缩小到原来的0.14倍
        HRimage.paste(day4bmp, (178,point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), daytemp[3])-20))
        #绘制白的温度折线
        drawred.line((90, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), daytemp[0]), 122, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), daytemp[1])), fill = 0)#白天第一条线
        drawred.line((122, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), daytemp[1]), 154, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), daytemp[2])), fill = 0)#白天第二条线
        drawred.line((154, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), daytemp[2]), 186, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), daytemp[3])), fill = 0)#白天第三条线
        #绘制夜间的温度折线
        drawblack.line((90, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), nighttemp[0]), 122, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), nighttemp[1])), fill = 0)#夜间第一条线
        drawblack.line((122, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), nighttemp[1]), 154, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), nighttemp[2])), fill = 0)#夜间第二条线
        drawblack.line((154, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), nighttemp[2]), 186, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), nighttemp[3])), fill = 0)#夜间第三条线
        #第一天显示气温
        drawred.text((88, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), daytemp[0])), str(daytemp[0]), font = font8, fill = 0)
        drawblack.text((88, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), nighttemp[0])), str(nighttemp[0]), font = font8, fill = 0)
        #第二天显示气温
        drawred.text((120, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), daytemp[1])), str(daytemp[1]), font = font8, fill = 0)
        drawblack.text((120, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), nighttemp[1])), str(nighttemp[1]), font = font8, fill = 0)
        #第三天显示气温
        drawred.text((152, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), daytemp[2])), str(daytemp[2]), font = font8, fill = 0)
        drawblack.text((152, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), nighttemp[2])), str(nighttemp[2]), font = font8, fill = 0)
        #第四天显示气温
        drawred.text((184, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), daytemp[3])), str(daytemp[3]), font = font8, fill = 0)
        drawblack.text((184, point_coordinate(min(daytemp + nighttemp), max(daytemp + nighttemp), nighttemp[3])), str(nighttemp[3]), font = font8, fill = 0)

        drawblack.text((78, 94), 'Update Time: ' + weather_info_base["lives"][0]["reporttime"], font = font8, fill = 0)    #绘制更新时间

        #check_battery() #检测电池剩余电量
        if (readCapacity(bus)>25):	#若电量多余25%，黑色字显示
                drawblack.text((7, 0), ("%5i%%" % readCapacity(bus)), font = font8, fill = 0)	#显示电量百分比
                drawblack.rectangle((0, 3, 0.08*readCapacity(bus), 5), fill = 0)	#绘制表示电量的长方形
        else:
                drawred.text((7, 0), ("%5i%%" % readCapacity(bus)), font = font8, fill = 0)	#电量少于25%，红色字显示
                drawred.rectangle((0, 3, 0.08*readCapacity(bus), 5), fill = 0)	#红色的长方形
        drawblack.rectangle((0, 2, 8, 6), outline = 0, width = 1)	#电量图标外框
        drawblack.rectangle((9, 3, 9, 5), fill = 0)	#电量图标右侧的小长方形

        #绘制WiFi图标
        drawblack.point((35,7))
        drawblack.arc((33, 5, 37, 9), start = 225, end = 315)
        drawblack.arc((31, 3, 39, 11), start = 225, end = 315)
        drawblack.arc((29, 1, 41, 13), start = 225, end = 315)
        if(not network):    #设备未联网
            #绘制红色叉
            drawred.line((32, 1, 38, 7))
            drawred.line((38, 1, 32, 7))

        show_on_epaper(HBimage, HRimage)    #在水墨屏上绘制图片
    except IOError as e:
        logging.info("Error:")
        logging.info(e)
        epd.init()
        epd.Clear()
        epd2in13bc.epdconfig.module_exit()
        exit()

def waiting():
    global network
    for i in range(60):    #每隔15s检测一次电量，共检测60次，也就是等待15min，期间不刷新屏幕
        logging.info("Check power: %5i%%" % readCapacity(bus))
        if(readCapacity(bus)<3.0):    #电量小于3%自动关机
            logging.info("Low power, shutdown.")
            epd.init()
            epd.Clear()
            epd2in13bc.epdconfig.module_exit()
            os.system("sudo poweroff")
        if(network == isNetOK(testserver=('restapi.amap.com',443))):    #若网络状态未改变
            time.sleep(15)    #睡眠15s
        else:    #若网络状态改变
            logging.info("The network state has changed.")
            network = isNetOK(testserver=('restapi.amap.com',443))    #更新网络状态
            break    #跳过所有睡眠
        if(os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/REFRESH")):    #php控制接口，若REFRESH文件存在，则刷新屏幕
            logging.info("REFRESH file request fresh.")
            os.remove(os.path.dirname(os.path.realpath(__file__)) + "/REFRESH")
            break

def main():
    try:
        while(True):
            show_weather(get_weather_info('base'), get_weather_info('all'))
            waiting()
    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd.init()
        epd.Clear()
        epd2in13bc.epdconfig.module_exit()
        exit()

if __name__ == "__main__":
    main()