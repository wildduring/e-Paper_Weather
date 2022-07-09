# e-Paper_Weather
Use raspberrypi zero to show weather info on e-Paper(2.13inch e-Paper HAT (B)).
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
#打开树莓派终端，并运行以下指令
sudo apt-get install wiringpi
#对于树莓派2019年5月之后的系统（早于之前的可不用执行），可能需要进行升级：
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
gpio -v
# 运行gpio -v会出现2.52版本，如果没有出现说明安装出错

#Bullseye分支系统使用如下命令：
git clone https://github.com/WiringPi/WiringPi
cd WiringPi
./build
gpio -v
# 运行gpio -v会出现2.60版本，如果没有出现说明安装出错
```
### For python3 we also need:
```
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install RPi.GPIO
sudo pip3 install spidev
```
## Installation
```
git clone https://github.com/wildduring/e-Paper_Weather.git
cd e-Paper_Weather
sudo make install
```
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