# e-Paper_Weather
Use raspberrypi zero to show weather info on e-Paper(2.13inch e-Paper HAT (B)).
![e-Paper_Weather](https://github.com/wildduring/e-Paper_Weather/blob/master/image/e-Paper_Weather.jpg)
## Hardware
### [UPS-Lite](https://github.com/linshuqin329/UPS-Lite)
![UPS-Lite_V1.2](https://github.com/wildduring/e-Paper_Weather/blob/master/image/UPS-Lite_V1.2.jpg)
### [2.13inch e-Paper HAT (B)](https://www.waveshare.net/wiki/2.13inch_e-Paper_HAT_(B))
![2.13inch-e-Paper-HAT-B-1](https://github.com/wildduring/e-Paper_Weather/blob/master/image/2.13inch-e-Paper-HAT-B-1.jpg)
![2.13inch-e-Paper-HAT-B-7](https://github.com/wildduring/e-Paper_Weather/blob/master/image/2.13inch-e-Paper-HAT-B-7.jpg)
## Dependencies
### BCM2835
```
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz
cd bcm2835-1.71/
sudo ./configure && sudo make && sudo make check && sudo make install
```
### wiringPi
```
#Open the raspberry pi terminal and run the following command
sudo apt-get install wiringpi
#For the system of raspberry pi after May 2019 (those earlier than that may not be implemented), it may need to be upgraded:
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
gpio -v
# Running `GPIO -v` will result in version 2.52. If there is no description, the installation error will appear

#The Bullseye branch system uses the following commands：
git clone https://github.com/WiringPi/WiringPi
cd WiringPi
./build
gpio -v
# Running `GPIO -v` will result in version 2.52. If there is no description, the installation error will appear
```
### For python3 we also need:
```
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install RPi.GPIO
sudo pip3 install spidev
sudo pip3 install struct smbus
```
## Installation
```
git clone https://github.com/wildduring/e-Paper_Weather.git
cd e-Paper_Weather
sudo make install
```
## How to run this demo?
First, we need a [amap](https://lbs.amap.com/) key, you can register an account by yourself.  
Second, put the key you obtained in the file './program/config/usr_key.ini'.  
Last, update the city code, you can get help from the [amap lib](https://lbs.amap.com/api/webservice/download).  
## Systemd service
Using the persistent [systemd](https://wiki.archlinux.org/title/systemd#Basic_systemctl_usage) service
### Start service immediately:
    sudo systemctl start e-Paper_weather.service
### Stop service immediately:
    sudo systemctl stop e-Paper_weather.service
### Start on boot:
    sudo systemctl enable e-Paper_weather.service
### Disable start on boot:
    sudo systemctl disable e-Paper_weather.service
### Check status:
    sudo systemctl status e-Paper_weather.service