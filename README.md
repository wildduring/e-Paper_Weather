# e-Paper_Weather  
Use raspberrypi zero to show weather info on e-Paper(2.13inch e-Paper HAT (B)).  
----------------------------------------------------------------------------------------------------------------------------  
##Installation  
(```)
git clone https://github.com/wildduring/e-Paper_Weather.git
cd e-Paper_Weather
sudo make install
(```)
##Systemd service  
----------------------------------------------------------------------------------------------------------------------------  
Using the persistent [systemd](https://wiki.archlinux.org/title/systemd#Basic_systemctl_usage) service  
##Start service immediately:  
'sudo systemctl start e-Paper_weather.service'  
##Stop service immediately:  
'sudo systemctl stop e-Paper_weather.service'  
##Start on boot:  
'sudo systemctl enable e-Paper_weather.service'  
##Disable start on boot:  
'sudo systemctl disable e-Paper_weather.service'  
##Check status:  
'sudo systemctl status e-Paper_weather.service'  