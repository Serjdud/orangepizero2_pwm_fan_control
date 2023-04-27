# Orangepi Zero 2 PWM FAN control
How to control a PWM fan depending on CPU temperature on a Orange Pi Zero 2? You can use one of four build in PWM.
You don't need any libraries, only python.

![OrangePi Zero2 fan](https://github.com/Serjdud/orangepizero2_pwm_fan_control/blob/main/img/pins.jpg)

## Prepare
1. Install [Python 3.7](https://www.python.org/) or higher.
2. Configure PWM on orangepi zero2. See section 3.20.5 in [user manual](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-Pi-Zero-2.html)
```
sudo nano /boot/orangepiEnv.txt
```
Add to the end of file ```pwm12``` or ```pwm34```.
```
overlays=pwm34
```
3. Reboot.
## Install
1. Clone repository.
```
git clone https://github.com/Serjdud/orangepizero2_pwm_fan_control.git
```
2. Move to source
```
./orangepizero2_pwm_fan_control
```
3. Make sh script executable
```
sudo chmod +x ./fan_control.sh
```
## Running
Run fan_control.sh with first argument = PWN nubmer. Wich PWM number you use depends on PWM pin. See picture above.
```
sudo ./fan_control.sh 3
```
To see other possible arguments run with -h argument
```
./fan_control.sh -h
```
## Autolaunch on system startup
1. Move to source (for example ```orangepizero2_pwm_fan_control``` installed to orangepi user's home directory)
```
cd ~/orangepizero2_pwm_fan_control
```
2. Get full path to fan_control.sh
```
pwd
```
> /home/orangepi/orangepizero2_pwm_fan_control
3. Copy the full path to the parameter ExecStart in ```fan_control.service``` and add PWM number argument.
```
sudo nano ./fan_control.service
```
```
ExecStart = /home/orangepi/orangepizero2_pwm_fan_control/fan_control.sh 3
```
4. Copy fan_control.service to daemon service folder (usually ```/etc/systemd/system/```).
```
sudo cp ./fan_control.service /etc/systemd/system/
```
5. Reload systemd config
```
sudo systemctl daemon-reload
```
6. Enable service autolaunch on system startup
```
sudo systemctl enable fan_control.service
```
7. Start service end check
```
sudo systemctl start fan_control.service
systemctl start fan_control.service
```